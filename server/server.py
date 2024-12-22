"""Home to the ``Server`` class."""

import logging
import pathlib
import secrets
import socket
import ssl
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
from src.packets.session_wrapper import SessionWrapper
from src.packets.type_wrapper import TypeWrapper
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
        socket.setdefaulttimeout(1)

        if not pathlib.Path("server_cert.pem").exists():
            logger.critical("No certificate file `server_cert.pem` found")
            raise SystemExit

        if not pathlib.Path("server_key.pem").exists():
            logger.critical("No certificate key file `server_key.pem` found")
            raise SystemExit

        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            certfile="server_cert.pem",
            keyfile="server_key.pem",
        )
        try:
            with ssl_context.wrap_socket(
                socket.create_server((self.hostname, self.port_number)),
                server_side=True,
            ) as welcoming_socket:
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
        """Generate a random session token.

        :return: A securely randomised token.
        """
        return secrets.token_bytes()

    def process_read_request(
        self,
        requestor_username: str | None,
        _packet: bytes,
    ) -> ReadResponse:
        """Respond to read requests.

        :param requestor_username: The username of the user requesting
        to read their messages.

        :param _packet: This parameter exists to fit the same signature
        as the other request processor functions.

        :return: The packet object to send in response to the read request.
        """
        if requestor_username is None:
            logger.info(
                "Received unauthenticated read request, responding without messages",
            )
            return ReadResponse([])

        messages = self.messages.get(requestor_username, []).copy()
        response = ReadResponse(messages)
        del self.messages.get(requestor_username, [])[: response.num_messages]

        logger.info(
            "%s message(s) delivered to %s",
            response.num_messages,
            requestor_username,
        )

        return response

    def process_create_request(
        self,
        requestor_username: str | None,
        packet: bytes,
    ) -> None:
        """Process create requests.

        :param requestor_username: The username of the user who sent the create request.
        :param packet: The packet provided by the client.
        """
        if requestor_username is None:
            logger.info("Received unauthenticated create request, ignoreing")
            return

        recipient_name, message = CreateRequest.decode_packet(packet)

        if recipient_name not in self.messages:
            self.messages[recipient_name] = []

        self.messages[recipient_name].append((requestor_username, message))
        logger.info(
            "Storing %s's message to %s",
            requestor_username,
            recipient_name,
        )

    def process_login_request(
        self,
        _requestor_username: str | None,
        packet: bytes,
    ) -> LoginResponse:
        """Process a client requset to login.

        :param _requestor_username: This parameter exists to fit the
        same signature as the other request processor functions.

        :param packet: The login requset packet to process.

        :return: The packet object to respond to the login request with.
        """
        (sender_name,) = LoginRequest.decode_packet(packet)

        if sender_name not in self.users:
            logger.info("Unregistered user %s attempted to login", sender_name)
            return LoginResponse(b"")

        session_token = self.generate_session_token()
        self.sessions[session_token] = sender_name
        logger.debug("Gave %s the token %s", sender_name, session_token)
        logger.info("Logged in %s", sender_name)

        senders_public_key = self.users[sender_name]
        encrypted_session_token = rsa.encrypt(session_token, senders_public_key)
        logger.debug("Encrypted token to %s", encrypted_session_token)

        return LoginResponse(encrypted_session_token)

    def process_registration_request(
        self,
        _requestor_username: str | None,
        packet: bytes,
    ) -> None:
        """Process a client request to register a new name.

        :param _requestor_username: This parameter exists to fit the
        same signature as the other request processor functions.

        :param packet: A byte array containing the registration request.
        """
        sender_name, public_key = RegistrationRequest.decode_packet(packet)

        if sender_name in self.users:
            message = f"Name {sender_name} already registered"
            logger.error(message)
            return

        self.users[sender_name] = public_key
        logger.info("Registered %s", sender_name)

    def process_key_request(
        self,
        _requestor_username: str | None,
        packet: bytes,
    ) -> KeyResponse:
        """Process a client request for a user's public key.

        :param _requestor_username: This parameter exists to fit the
        same signature as the other request processor functions.

        :param packet: A byte array containing the key request.

        :return: The packet object to respond to the key request with.
        """
        (requested_user,) = KeyRequest.decode_packet(packet)
        logger.info("Received request for %s's key", requested_user)

        if requested_user not in self.users:
            logger.info("%s is not registered, sending empty response", requested_user)
            return KeyResponse(None)

        public_key = self.users[requested_user]
        logger.info("Responding with %s's key", requested_user)
        return KeyResponse(public_key)

    def process_request(
        self,
        packet: bytes,
        connection_socket: socket.socket,
    ) -> None:
        """Process an incoming client request.

        :param packet: The packet received from a client.
        :param connection_socket: The socket to use for responding to read requests.
        """
        message_type, packet = TypeWrapper.decode_packet(packet)
        session_token, packet = SessionWrapper.decode_packet(packet)

        if session_token is not None:
            requestor_username = self.sessions.get(session_token, None)
        else:
            requestor_username = None

        if message_type not in PROCESS_REQUEST_MAPPING:
            logging.error("Message of incorrect type received!")
            return

        logger.info("Received %s request", message_type.name)

        processor_function = PROCESS_REQUEST_MAPPING[message_type]
        response = processor_function(self, requestor_username, packet)

        if response is not None:
            response_type = REQUEST_RESPONSE_MAPPING[message_type]
            packet = TypeWrapper(response_type, response).to_bytes()
            connection_socket.sendall(packet)

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

        logger.info("\nNew client connection from %s", client_address)

        try:
            with connection_socket:
                packet = connection_socket.recv(4096)
                self.process_request(packet, connection_socket)

        except TimeoutError:
            error_message = "Timed out while waiting for request"
            logger.exception(error_message)
        except ValueError:
            error_message = "Request discarded"
            logger.exception(error_message)

    def stop(self) -> None:
        """Stop the server."""
        logger.info("Stopping server.")
        self.running = False


ServerProcessFunction: TypeAlias = Callable[[Server, str | None, bytes], Packet | None]
PROCESS_REQUEST_MAPPING: Final[Mapping[MessageType, ServerProcessFunction]] = {
    MessageType.REGISTER: Server.process_registration_request,
    MessageType.LOGIN: Server.process_login_request,
    MessageType.KEY: Server.process_key_request,
    MessageType.CREATE: Server.process_create_request,
    MessageType.READ: Server.process_read_request,
}

REQUEST_RESPONSE_MAPPING: Final[Mapping[MessageType, MessageType]] = {
    MessageType.LOGIN: MessageType.LOGIN_RESPONSE,
    MessageType.KEY: MessageType.KEY_RESPONSE,
    MessageType.READ: MessageType.READ_RESPONSE,
}
