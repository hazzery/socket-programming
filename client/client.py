"""The client module contains the Client class."""

import logging
import pathlib
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
from src.packets.read_request import ReadRequest
from src.packets.read_response import ReadResponse
from src.packets.registration_request import RegistrationRequest
from src.packets.session_wrapper import SessionWrapper
from src.packets.type_wrapper import TypeWrapper
from src.receive_all import receive_all

# Buffer size chosen as per note in docs:
# https://docs.python.org/3/library/socket.html#socket.socket.recv
RECEIVE_BUFFER_SIZE = 4096

logger = logging.getLogger(__name__)

socket.setdefaulttimeout(1)


class Client:
    """Send and receives messages to and from the server."""

    def __init__(
        self,
        hostname: str,
        port_number: int,
        username: str,
        *,
        connection_socket: socket.socket | None = None,
    ) -> None:
        """Initialise the client with specified arguments.

        :param hostname: The address which the server is hosted on. Can
        be an IPv4 or IPv6 address, a domain name, or "localhost".

        :param port_number: The port number which the server is
        listening on. Can be from 1024 to 6400 (inclusive).

        :param username: The name of the user wanting to connect.

        :param connection_socket: The socket to communicate with the server on.
        """
        self.user_name = username

        logger.debug(
            "Client for %s port %s created by %s",
            hostname,
            port_number,
            username,
        )

        self.public_key, self.__private_key = rsa.newkeys(512)

        logger.debug(
            "Created key %s for user %s",
            (self.public_key.n, self.public_key.e),
            self.user_name,
        )

        self.session_token: bytes | None = None
        self.key_cache: dict[str, rsa.PublicKey] = {}
        self.connection_socket = connection_socket or self.secure_connection(
            hostname,
            port_number,
            "server_cert.pem",
        )

    def secure_connection(
        self,
        hostname: str,
        port_number: int,
        cafile: str,
    ) -> ssl.SSLSocket:
        """Create a default context SSLSocket and connect to the server.

        :param hostname: The address which the server is hosted on. Can
        be an IPv4 or IPv6 address, a domain name, or "localhost".

        :param port_number: The port number which the server is
        listening on. Can be from 1024 to 6400 (inclusive).

        :param cafile: The server's SSL certificate in PEM format.
        Defaults to ``None``.

        :return: The secure socket object.
        """
        if cafile is not None and not pathlib.Path(cafile).exists():
            message = f"No server certificate file `{cafile}` found"
            logger.critical(message)
            raise SystemExit

        ssl_context = ssl.create_default_context()
        ssl_context.load_verify_locations(cafile=cafile)

        connection_socket = socket.socket()
        secure_socket = ssl_context.wrap_socket(
            connection_socket,
            server_hostname=hostname,
        )
        secure_socket.connect((hostname, port_number))
        return secure_socket

    def send_request(
        self,
        request: Packet,
        message_type: MessageType,
        *,
        expect_response: bool = True,
    ) -> tuple[MessageType, bytes] | tuple[None, None]:
        """Send a request to the server and optionally await its response.

        :param request: The packet object containing request to be sent.
        :param message_type: The type of message contained in ``request``.
        :param expect_response: Set this value to ``False`` to prevent a read
        from the connection socket. Defaults to ``True``.

        :return: A tuple containing the type of the server's response
        message and the response as a byte string. Both values will be
        ``None`` if ``expect_response`` is set to False.
        """
        packet = TypeWrapper(
            message_type,
            SessionWrapper(self.session_token, request),
        ).to_bytes()

        try:
            self.connection_socket.send(packet)

            if not expect_response:
                return None, None

            response_packet = receive_all(self.connection_socket, RECEIVE_BUFFER_SIZE)

        except (ConnectionRefusedError, TimeoutError) as error:
            message = (
                "Connection refused, likely due to invalid port number"
                if isinstance(error, ConnectionRefusedError)
                else "Connection timed out, likely due to invalid host name"
            )
            logger.exception(message)
            raise SystemExit from error

        response = TypeWrapper.decode_packet(response_packet)

        logger.info(
            "%s record sent as %s",
            message_type.name.capitalize(),
            self.user_name,
        )

        return response

    def send_registration_request(self) -> None:
        """Send a registration request to the server."""
        request = RegistrationRequest(self.user_name, self.public_key)
        self.send_request(request, MessageType.REGISTER, expect_response=False)

    def send_login_request(self) -> bytes:
        """Send a login request to the server.

        :raises RuntimeError: If the server sends an incorrect response.
        :return: The LoginResponse packet from the server.
        """
        request = LoginRequest(self.user_name)
        message_type, payload = self.send_request(request, MessageType.LOGIN)

        if payload is None:
            raise RuntimeError("No response received from server")

        if message_type != MessageType.LOGIN_RESPONSE:
            raise RuntimeError("Received incorrect type response from server")

        (encrypted_session_token,) = LoginResponse.decode_packet(payload)
        logger.debug("Received encrypted token bytes %s", encrypted_session_token)

        if len(encrypted_session_token) == 0:
            logger.error("You are not registered! Please register before logging in")
            raise SystemExit

        self.session_token = rsa.decrypt(encrypted_session_token, self.__private_key)
        logger.debug("Storing provided session token %s", self.session_token)
        logger.info("Now logged in as %s", self.user_name)

        return payload

    def send_key_request(self, receiver_name: str | None = None) -> bytes:
        """Send a public key request to the server.

        :param receiver_name: The name of the user whose key should be
        requested. Will request from ``stdin`` if not present.

        :return: The ``KeyResponse`` packet from the server.
        """
        if not receiver_name:
            receiver_name = input("Who's key are we requesting? ")

        request = KeyRequest(receiver_name)
        message_type, payload = self.send_request(request, MessageType.KEY)

        if payload is None:
            raise RuntimeError("No response received from the server")

        if message_type != MessageType.KEY_RESPONSE:
            logger.error("Received incorrect type response from server")
            raise SystemExit

        (public_key,) = KeyResponse.decode_packet(payload)

        if public_key is None:
            logger.warning("The requested user is not registered")
        else:
            self.key_cache[receiver_name] = public_key
            logger.info("Received %s's key", receiver_name)

        return payload

    def send_create_request(
        self,
        receiver_name: str | None = None,
        message: str | None = None,
    ) -> None:
        """Send a create request to the server.

        :param receiver_name: The name of the person to send the message
        to. Will request from ``stdin`` if not present.

        :param message: The message to be sent. Will request from
        ``stdin`` if not present.
        """
        if self.session_token is None:
            logger.error("Please log in before sending messages")
            return

        if receiver_name is None:
            receiver_name = input("Enter the name of the receiver: ")

        if receiver_name not in self.key_cache:
            logger.error("Perform key request for user before sending message.")
            return

        if message is None:
            message = input("Enter the message to be sent: ")

        logger.debug(
            'User specified message to %s: "%s"',
            receiver_name,
            message,
        )

        encrypted_message = rsa.encrypt(message.encode(), self.key_cache[receiver_name])

        request = CreateRequest(receiver_name, encrypted_message)
        self.send_request(request, MessageType.CREATE, expect_response=False)

    def read_message_response(self, packet: bytes) -> None:
        """Read a message response from the server.

        :param packet: The message response from the server.
        """
        messages, more_messages = ReadResponse.decode_packet(packet)

        for sender, encrypted_message in messages:
            message_bytes = rsa.decrypt(encrypted_message, self.__private_key)
            logger.info(
                "\nMessage from %s:\n%s",
                sender,
                message_bytes.decode(),
            )

        if len(messages) == 0:
            logger.info("No messages available")
        elif more_messages:
            logger.info("More messages available, please send another request")

    def send_read_request(self) -> bytes | None:
        """Send a read request to the server.

        :raises RuntimeError: If the server sends an invalid response.
        :return: The ReadResponse packet received from the server.
        """
        if self.session_token is None:
            logger.error("Please log in to request messages")
            return None

        request = ReadRequest()
        message_type, payload = self.send_request(request, MessageType.READ)

        if payload is None:
            raise RuntimeError("No response received from the server")

        if message_type != MessageType.READ_RESPONSE:
            raise RuntimeError("Incorrect type message received from the server.")

        self.read_message_response(payload)

        return payload

    def run(self) -> None:
        """Ask the user to input message and send request to server."""
        help_text = (
            "'register': Register your name and public key with the server.\n"
            "'login': Get a token from the server for sending and receiving messages.\n"
            "'key': Request a user's public key so you can send them messages.\n"
            "'create': Send a message to another user.\n"
            "'read': Get all messages sent to you.\n"
            "'help': Show this message.\n"
            "'exit': Quit the application.\n"
        )

        logger.info(help_text)

        while True:
            user_input = input("Please enter a request type: ")

            if user_input == "exit":
                return

            if user_input == "help":
                logger.info(help_text)
                continue

            try:
                message_type = MessageType.from_str(user_input)
            except ValueError:
                logger.warning("Invalid message type")
                continue

            if message_type not in SEND_REQUEST_MAPPING:
                logging.warning("Given message type is not a valid request!")
                continue

            send_function = SEND_REQUEST_MAPPING[message_type]
            send_function(self)


ClientSendFunction: TypeAlias = Callable[[Client], bytes | None]
SEND_REQUEST_MAPPING: Final[Mapping[MessageType, ClientSendFunction]] = {
    MessageType.REGISTER: Client.send_registration_request,
    MessageType.LOGIN: Client.send_login_request,
    MessageType.KEY: Client.send_key_request,
    MessageType.CREATE: Client.send_create_request,
    MessageType.READ: Client.send_read_request,
}
