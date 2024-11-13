"""The client module contains the Client class."""

import logging
import socket
from collections import OrderedDict

from message_cipher.rsa_system import RSA

from src.command_line_application import CommandLineApplication
from src.message_type import MessageType
from src.packets.create_request import CreateRequest
from src.packets.key_request import KeyRequest
from src.packets.key_response import KeyResponse
from src.packets.packet import Packet
from src.packets.read_request import ReadRequest
from src.packets.read_response import ReadResponse
from src.packets.registration_request import RegistrationRequest
from src.port_number import PortNumber

logger = logging.getLogger(__name__)


class Client(CommandLineApplication):
    """Send and receives messages to and from the server."""

    MAX_USERNAME_LENGTH = 255

    def __init__(self, arguments: list[str]) -> None:
        """Initialise the client with specified arguments.

        :param arguments: A list containing the host name, port number,
        username, and message type.
        """
        super().__init__(
            OrderedDict(
                host_name=self.parse_hostname,
                port_number=PortNumber,
                user_name=self.parse_username,
                message_type=MessageType.from_str,
            ),
        )

        parsed_arguments: tuple[str, PortNumber, str, MessageType]
        parsed_arguments = self.parse_arguments(arguments)

        self.host_name, self.port_number, self.user_name, self.message_type = (
            parsed_arguments
        )

        logger.info(
            "Client for %s port %s created by %s to send %s request",
            self.host_name,
            self.port_number,
            self.user_name,
            self.message_type.name.lower(),
        )

        self.receiver_name = ""
        self.message = ""
        self.response: bytes | None = None

    @staticmethod
    def parse_hostname(host_name: str) -> str:
        """Parse the host name, ensuring it is valid.

        :param host_name: String representing the host name.
        :return: String of the host name.
        :raises ValueError: If the host name is invalid.
        """
        try:
            socket.getaddrinfo(host_name, 1024)
        except socket.gaierror as error:
            message = (
                'Invalid host name, must be an IP address, domain name, or "localhost"'
            )
            logger.exception(message)
            raise ValueError(message) from error

        return host_name

    @staticmethod
    def parse_username(user_name: str) -> str:
        """Parse the username, ensuring it is valid.

        :param user_name: String representing the username.
        :return: String of the username.
        :raises ValueError: If the username is invalid.
        """
        if len(user_name) == 0:
            logger.error("Username is empty")
            raise ValueError("Username must not be empty")

        if len(user_name.encode()) > Client.MAX_USERNAME_LENGTH:
            logger.error("Username consumes more than 255 bytes")
            raise ValueError("Username must consume at most 255 bytes")

        return user_name

    def send_request(self, request: Packet, *, expect_response: bool = True) -> bytes:
        """Send a message request record to the server.

        :param request: The message request to be sent.
        :return: The server's response if applicable, otherwise ``None``.
        """
        response = b""
        packet = request.to_bytes()
        try:
            with socket.socket() as connection_socket:
                connection_socket.settimeout(1)
                connection_socket.connect((self.host_name, self.port_number))
                connection_socket.send(packet)
                if expect_response:
                    response = connection_socket.recv(4096)

        except (ConnectionRefusedError, TimeoutError) as error:
            message = (
                "Connection refused, likely due to invalid port number"
                if isinstance(error, ConnectionRefusedError)
                else "Connection timed out, likely due to invalid host name"
            )
            logger.exception(message)
            print(message)
            raise SystemExit from error

        logger.info(
            "%s record sent as %s",
            self.message_type.name.lower(),
            self.user_name,
        )
        print(f"{self.message_type.name.lower()} record sent as {self.user_name}")

        return response

    @staticmethod
    def read_message_response(packet: bytes) -> None:
        """Read a message response from the server.

        :param packet: The message response from the server.
        """
        _, packet = Packet.decode_packet(packet)
        messages, more_messages = ReadResponse.decode_packet(packet)

        for sender, message in messages:
            logger.info('Received %s\'s message "%s"', sender, message)
            print(f"Message from {sender}:\n{message}\n")

        if len(messages) == 0:
            logger.info("Response contained no messages")
            print("No messages available")
        elif more_messages:
            logger.info("Server has more messages available for this user")
            print("More messages available, please send another request")

    def send_read_request(self) -> None:
        """Send a read request to the server."""
        request = ReadRequest(self.user_name)
        self.response = self.send_request(request)

        self.read_message_response(self.response)

    def send_create_request(
        self,
        receiver_name: str | None,
        message: str | None,
    ) -> None:
        """Send a create request to the server.

        :param receiver_name: The name of the person to send the messag to.
        :param message: The message to be sent.
        """
        if receiver_name is None:
            self.receiver_name = input("Enter the name of the receiver: ")
        else:
            self.receiver_name = receiver_name

        if message is None:
            self.message = input("Enter the message to be sent: ")
        else:
            self.message = message

        logger.info(
            'User specified message to %s: "%s"',
            self.receiver_name,
            self.message,
        )

        request = CreateRequest(
            self.user_name,
            self.receiver_name,
            self.message,
        )
        self.send_request(request)

    def send_login_request(self) -> None:
        """Send a login request to the server."""
        print("logging in")

    def send_registration_request(self) -> None:
        """Send a login request to the server."""
        public_key, private_key = RSA()

        print(f"Creatged product {public_key.product}")
        print(f"Created exponent {public_key.exponent}")

        request = RegistrationRequest(self.user_name, public_key)
        self.send_request(request)

    def send_key_request(self, receiver_name: str | None) -> None:
        """Send a pubblic key request to the server."""
        if not receiver_name:
            receiver_name = input("Who's key are we requesting?")

        request = KeyRequest(receiver_name)
        response = self.send_request(request)
        message_type, payload = Packet.decode_packet(response)
        if message_type != MessageType.KEY_RESPONSE:
            raise ValueError("Wrong response type!")

        (public_key,) = KeyResponse.decode_packet(payload)
        print(f"Received product {public_key.product}")
        print(f"Received exponent {public_key.exponent}")

    def run(
        self,
        *,
        receiver_name: str | None = None,
        message: str | None = None,
    ) -> None:
        """Ask the user to input message and send request to server.

        :param receiver_name: The name of the user to send the message to.
        Will request from ``stdin`` if not present. Defaults to ``None``.
        :param message: The message to send. Will request from
        ``stdin`` if not present. Defaults to ``None``.
        """
        match self.message_type:
            case MessageType.READ:
                self.send_read_request()

            case MessageType.CREATE:
                self.send_create_request(receiver_name, message)

            case MessageType.LOGIN:
                self.send_login_request()

            case MessageType.REGISTER:
                self.send_registration_request()

            case MessageType.KEY_REQUEST:
                self.send_key_request(receiver_name)

            case _:
                print("Oopsies, wrong message type!")

    @property
    def result(self) -> bytes:
        """Get the packet received from the server.

        This property must only be used after calling ``run()``
        otherwise no response will exist!

        :raises RuntimeError: When there was no response.
        Will always occur if requested before call to ``run()``.

        :return: A bytes object of the server's response.
        """
        if self.response is None:
            raise RuntimeError("No response! Was result requested after call to run()?")

        return self.response
