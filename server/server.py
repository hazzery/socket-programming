"""Home to the ``Server`` class."""

import logging
import secrets
import socket
from collections import OrderedDict
from collections.abc import Callable, Mapping
from typing import Final, TypeAlias

import rsa

from src.command_line_application import CommandLineApplication
from src.message_type import MessageType
from src.packets.create_request import CreateRequest
from src.packets.key_request import KeyRequest
from src.packets.key_response import KeyResponse
from src.packets.login_request import LoginRequest
from src.packets.login_response import LoginResponse
from src.packets.packet import Packet
from src.packets.read_response import ReadResponse
from src.packets.registration_request import RegistrationRequest
from src.port_number import PortNumber

logger = logging.getLogger(__name__)


class Server(CommandLineApplication):
    """A server side program that receives messages from clients and stores them.

    The server can be run with ``python3 -m server <port number>``.
    """

    def __init__(self, arguments: list[str]) -> None:
        """Initialise the server with a specified port number.

        :param arguments: The program arguments from the command line.
        """
        super().__init__(OrderedDict(port_number=PortNumber))

        self.port_number: PortNumber
        (self.port_number,) = self.parse_arguments(arguments)

        self.running = True
        self.hostname = "localhost"
        self.users: dict[str, rsa.PublicKey] = {}
        self.sessions: dict[bytes, str] = {}
        self.messages: dict[str, list[tuple[str, bytes]]] = {}

    def run(self) -> None:
        """Initiate the welcoming socket and start main event loop.

        :raise SystemExit: If the socket fails to connect
        """
        try:
            # Create a TCP/IP socket
            with socket.socket() as welcoming_socket:
                welcoming_socket.settimeout(1)
                welcoming_socket.bind((self.hostname, self.port_number))
                # A maximum, of five unprocessed connections are allowed
                welcoming_socket.listen(5)
                logger.info(
                    "Server started on %s port %s",
                    self.hostname,
                    self.port_number,
                )

                while self.running:
                    self.run_server(welcoming_socket)

        except OSError as error:
            message = "Error binding socket on provided port"
            logger.exception(message)
            raise SystemExit from error

    @staticmethod
    def generate_session_token() -> bytes:
        """Generate a random session token."""
        return secrets.token_bytes()

    def process_read_request(
        self,
        requestor_username: str | None,
        _packet: bytes,
    ) -> bytes:
        """Respond to read requests.

        :param packet: The read request packet to process.
        :param connection_socket: The connection socket to send the response on.
        """
        if requestor_username is None:
            logger.info(
                "Received unauthenticated read request, responding without messages",
            )
            return ReadResponse([]).to_bytes()

        messages = self.messages.get(requestor_username, []).copy()
        response = ReadResponse(messages)
        del self.messages.get(requestor_username, [])[: response.num_messages]

        logger.info(
            "%s message(s) delivered to %s",
            response.num_messages,
            requestor_username,
        )

        return response.to_bytes()

    def process_create_request(
        self,
        requestor_username: str | None,
        packet: bytes,
    ) -> None:
        """Process create requests.

        :param session_token: The token provided by the client.
        :param packet: The packet provided by the client.
        """
        if requestor_username is None:
            logger.info("Received unauthenticated create request, ignoreing")
            return

        receiver_name, message = CreateRequest.decode_packet(packet)

        if receiver_name not in self.messages:
            self.messages[receiver_name] = []

        self.messages[receiver_name].append((requestor_username, message))
        logger.info(
            'Storing %s\'s message to %s: "%s"',
            requestor_username,
            receiver_name,
            message.decode(),
        )

    def process_login_request(
        self,
        _requestor_username: str | None,
        packet: bytes,
    ) -> bytes:
        """Process a client requset to login.

        :param packet: A byte array containing the login request.
        """
        (sender_name,) = LoginRequest.decode_packet(packet)

        if sender_name not in self.users:
            logger.info("Unregistered user %s attempted to login", sender_name)
            return LoginResponse(b"").to_bytes()

        session_token = self.generate_session_token()
        self.sessions[session_token] = sender_name
        logger.debug("Gave %s the token %s", sender_name, session_token)

        senders_public_key = self.users[sender_name]
        encrypted_session_token = rsa.encrypt(session_token, senders_public_key)
        logger.debug("Encrypted token to %s", encrypted_session_token)

        return LoginResponse(encrypted_session_token).to_bytes()

    def process_registration_request(
        self,
        _requestor_username: str | None,
        packet: bytes,
    ) -> None:
        """Process a client request to register a new name.

        :param packet: A byte array containing the registration request.
        """
        sender_name, public_key = RegistrationRequest.decode_packet(packet)

        if sender_name in self.users:
            message = f"Name {sender_name} already registered"
            logger.error(message)
            return

        self.users[sender_name] = public_key
        logger.info(
            "Registered %s with key %s",
            sender_name,
            (public_key.n, public_key.e),
        )

    def process_key_request(
        self,
        _requestor_username: str | None,
        packet: bytes,
    ) -> bytes:
        """Process a client request for a user's public key.

        :param packet: A byte array containing the key request.
        :param connection_socket: The socket to send the response over.
        """
        (requested_user,) = KeyRequest.decode_packet(packet)
        logger.info("Received request for %s's key", requested_user)

        if requested_user not in self.users:
            return KeyResponse(None).to_bytes()

        public_key = self.users[requested_user]
        return KeyResponse(public_key).to_bytes()

    def process_request(self, packet: bytes, connection_socket: socket.socket) -> None:
        """Process an incoming client request.

        :param packet: The packet received from a client.
        :param connection_socket: The socket to use for responding to read requests.
        """
        message_type: MessageType
        session_token: bytes | None

        message_type, session_token, packet = Packet.decode_packet(packet)

        if session_token is not None:
            requestor_username = self.sessions.get(session_token, None)
        else:
            requestor_username = None

        if message_type not in PROCESS_REQUEST_MAPPING:
            logging.error("Message of incorrect type received!")
            return

        processor_function = PROCESS_REQUEST_MAPPING[message_type]
        response = processor_function(self, requestor_username, packet)

        if response is not None:
            connection_socket.send(response)

    def run_server(self, welcoming_socket: socket.socket) -> None:
        """Run the server side of the program.

        :param welcoming_socket: The welcoming socket to accept connections on
        """
        try:
            connection_socket, client_address = welcoming_socket.accept()
        except TimeoutError:
            # Prevent the server from indefinitely waiting for new
            # client requests, so that the ``stop`` function works
            return

        connection_socket.settimeout(1)

        logger.info("\nNew client connection from %s", client_address)

        try:
            with connection_socket:
                record = connection_socket.recv(4096)
                self.process_request(record, connection_socket)

        except TimeoutError:
            error_message = "Timed out while waiting for message request"
            logger.exception(error_message)
        except ValueError:
            error_message = "Message request discarded"
            logger.exception(error_message)

    def stop(self) -> None:
        """Stop the server."""
        logger.info("Stopping server.")
        self.running = False


ServerProcessFunction: TypeAlias = Callable[[Server, str | None, bytes], bytes | None]
PROCESS_REQUEST_MAPPING: Final[Mapping[MessageType, ServerProcessFunction]] = {
    MessageType.REGISTER: Server.process_registration_request,
    MessageType.LOGIN: Server.process_login_request,
    MessageType.KEY: Server.process_key_request,
    MessageType.CREATE: Server.process_create_request,
    MessageType.READ: Server.process_read_request,
}
