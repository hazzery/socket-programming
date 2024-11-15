"""Home to the ``Server`` class."""

import logging
import secrets
import socket
from collections import OrderedDict

import rsa

from src.command_line_application import CommandLineApplication
from src.message_type import MessageType
from src.packets.create_request import CreateRequest
from src.packets.key_request import KeyRequest
from src.packets.key_response import KeyResponse
from src.packets.login_request import LoginRequest
from src.packets.login_response import LoginResponse
from src.packets.packet import Packet
from src.packets.read_request import ReadRequest
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

        # pylint thinks that self.parse_arguments is only
        # capable of returning an empty list
        # pylint: disable=unbalanced-tuple-unpacking
        (self.port_number,) = self.parse_arguments(arguments)

        self.running = True
        self.hostname = "localhost"
        self.users: dict[str, rsa.PublicKey] = {}
        self.sessions: dict[str, bytes] = {}
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
    def send_response(response: Packet, connection_socket: socket.socket) -> None:
        """Send a response to the client's request.

        :param response: The response object.
        :param connection_socket: The socket to send the response over.
        """
        record = response.to_bytes()
        connection_socket.send(record)

    @staticmethod
    def generate_session_token() -> bytes:
        """Generate a random session token."""
        return secrets.token_bytes()

    def process_read_request(
        self,
        packet: bytes,
        connection_socket: socket.socket,
    ) -> None:
        """Respond to read requests.

        :param packet: The read request packet to process.
        :param connection_socket: The connection socket to send the response on.
        """
        (sender_name,) = ReadRequest.decode_packet(packet)

        response = ReadResponse(self.messages.get(sender_name, []))
        self.send_response(response, connection_socket)

        del self.messages.get(sender_name, [])[: response.num_messages]
        logger.info(
            "%s message(s) delivered to %s",
            response.num_messages,
            sender_name,
        )

    def process_create_request(
        self,
        packet: bytes,
    ) -> None:
        """Process create requests.

        :param sender_name: The name of the user who sent the create request.
        :param receiver_name: The name of the user who will receive the message.
        :param message: The message to be sent.
        """
        (
            sender_name,
            receiver_name,
            message,
        ) = CreateRequest.decode_packet(packet)

        if receiver_name not in self.messages:
            self.messages[receiver_name] = []

        self.messages[receiver_name].append((sender_name, message))
        logger.info(
            'Storing %s\'s message to %s: "%s"',
            sender_name,
            receiver_name,
            message.decode(),
        )

    def process_login_request(
        self,
        packet: bytes,
        connection_socket: socket.socket,
    ) -> None:
        """Process a client requset to login.

        :param packet: A byte array containing the login request.
        """
        (sender_name,) = LoginRequest.decode_packet(packet)

        if sender_name not in self.users:
            response = LoginResponse(b"")
            self.send_response(response, connection_socket)
            logger.info("Unregistered user %s attempted to login", sender_name)
            return

        session_token = self.generate_session_token()
        self.sessions[sender_name] = session_token
        logger.debug("Gave %s the token %s", sender_name, session_token)

        senders_public_key = self.users[sender_name]
        encrypted_session_token = rsa.encrypt(session_token, senders_public_key)
        logger.debug("Encrypted token to %s", encrypted_session_token)
        response = LoginResponse(encrypted_session_token)
        self.send_response(response, connection_socket)

    def process_registration_request(self, packet: bytes) -> None:
        """Process a client request to register a new name.

        :param packet: A byte array containing the registration request.
        """
        sender_name, public_key = RegistrationRequest.decode_packet(packet)
        if sender_name not in self.users:
            self.users[sender_name] = public_key
            logger.info(
                "Registered %s with key %s",
                sender_name,
                (public_key.n, public_key.e),
            )

        else:
            message = f"name {sender_name} already registered"
            logger.error(message)

    def process_key_request(
        self,
        packet: bytes,
        connection_socket: socket.socket,
    ) -> None:
        """Process a client request for a user's public key.

        :param packet: A byte array containing the key request.
        :param connection_socket: The socket to send the response over.
        """
        (requested_user,) = KeyRequest.decode_packet(packet)
        logger.info("Received request for %s's key", requested_user)

        public_key = self.users[requested_user]
        response = KeyResponse(public_key)
        self.send_response(response, connection_socket)

    def process_request(self, packet: bytes, connection_socket: socket.socket) -> None:
        """Process an incoming client request.

        :param packet: The packet received from a client.
        :param connection_socket: The socket to use for responding to read requests.
        """
        message_type: MessageType
        message_type, packet = Packet.decode_packet(packet)

        match message_type:
            case MessageType.READ:
                self.process_read_request(packet, connection_socket)

            case MessageType.CREATE:
                self.process_create_request(packet)

            case MessageType.LOGIN:
                self.process_login_request(packet, connection_socket)

            case MessageType.REGISTER:
                self.process_registration_request(packet)

            case MessageType.KEY_REQUEST:
                self.process_key_request(packet, connection_socket)

            case _:
                logging.error("Message of incorrect type received!")

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
