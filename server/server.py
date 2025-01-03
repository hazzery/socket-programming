"""Home to the ``Server`` class."""

import logging
import pathlib
import secrets
import selectors
import socket
import ssl
from collections.abc import Callable, Mapping
from typing import Final, TypeAlias

import rsa

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
from src.receive_all import receive_all

RECEIVE_BUFFER_SIZE = 4096

logger = logging.getLogger(__name__)


class Server:
    """A server side program that receives messages from clients and stores them.

    The server can be run with ``python3 -m server <hostname> <port number>``.
    """

    def __init__(self, hostname: str, port_number: int) -> None:
        """Initialise the server with a specified port number.

        :param hostname: The address to host the server on.
        :param port_number: The port number for the server to be exposed on.
        """
        self.hostname = hostname
        self.port_number = port_number

        self.running = True
        self.selector = selectors.DefaultSelector()

        self.users: dict[str, rsa.PublicKey] = {}
        self.sessions: dict[bytes, str] = {}
        self.messages: dict[str, list[tuple[str, bytes]]] = {}

    def secure_socket(
        self,
        *,
        certificate: str,
        key: str,
    ) -> ssl.SSLSocket:
        """Create a new SSL socket using the certificate and key on the disk.

        :param certificate: A path to a PEM enccoded SSL certificate.
        :param key: A path to a PEM encoded SSL certificate private key.

        :return: An SSL socket object configured as the Server's welcoming socket.
        """
        if not pathlib.Path(certificate).exists():
            message = f"No certificate file `{certificate}` found"
            logger.critical(message)
            raise SystemExit

        if not pathlib.Path(key).exists():
            message = f"No certificate key file `{key}` found"
            logger.critical(message)
            raise SystemExit

        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            certfile=certificate,
            keyfile=key,
        )

        try:
            return ssl_context.wrap_socket(
                socket.create_server((self.hostname, self.port_number)),
                server_side=True,
            )
        except OSError as error:
            logger.critical(
                "Error binding socket on provided address %s:%d",
                self.hostname,
                self.port_number,
            )
            logger.debug("", exc_info=True)
            raise SystemExit from error

    def accept_connection(self, welcoming_socket: socket.socket) -> None:
        """Accept a new client connection and register a callback.

        :param welcoming_socket: The socket with an incoming connection reqeust.
        """
        connection_socket, client_address = welcoming_socket.accept()

        logger.info("\nNew client connection from %s", client_address)

        self.selector.register(
            connection_socket,
            selectors.EVENT_READ,
            self.run_server,
        )

    def run(
        self,
        *,
        welcoming_socket: socket.socket | None = None,
        certificate: str | None = None,
        key_file: str | None = None,
    ) -> None:
        """Initiate the welcoming socket and start main event loop.

        Note: Must specify ``welcoming_socket`` or both ``certificate``
        and ``key_file``. Specifying an incorrect set of these
        parameters will raise a ValueError.

        :param welcoming_socket: The socket to initialise as the
        server's welcoming socket. Leave unspecified or ``None`` to
        create a new SSL socket to use.

        :param certificate: A path to a PEM enccoded SSL certificate.
        :param key: A path to a PEM encoded SSL certificate private key.
        """
        if (not welcoming_socket and not (certificate and key_file)) or (
            welcoming_socket and (certificate or key_file)
        ):
            logger.error(
                "Must specify welcoming_socket, or both of certificate and key_file",
            )
            raise ValueError

        if certificate and key_file:
            welcoming_socket = self.secure_socket(
                certificate=certificate,
                key=key_file,
            )
        elif not welcoming_socket:
            # This will never execute becuase of the initial if check
            # which raises an exception. However, having this here
            # pleases the type checker.
            return

        logger.info(
            "Server started on %s port %s",
            self.hostname,
            self.port_number,
        )

        welcoming_socket.setblocking(False)  # noqa: FBT003
        self.selector.register(
            welcoming_socket,
            selectors.EVENT_READ,
            self.accept_connection,
        )

        while self.running:
            for key, _mask in self.selector.select():
                callback = key.data
                callback(key.fileobj)

        welcoming_socket.close()

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

    def run_server(self, connection_socket: socket.socket) -> None:
        """Receive and process an incoming client request.

        :param connection_socket: A socket connected to a client instance.
        """
        try:
            packet = receive_all(connection_socket, RECEIVE_BUFFER_SIZE)
            if len(packet) == 0:
                connection_socket.close()
                logger.info("Closed client connection")
                self.selector.unregister(connection_socket)
                return

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
