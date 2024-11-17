"""The client module contains the Client class."""

import logging
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
from src.packets.read_request import ReadRequest
from src.packets.read_response import ReadResponse
from src.packets.registration_request import RegistrationRequest
from src.parse_hostname import parse_hostname
from src.parse_username import parse_username
from src.port_number import PortNumber

logger = logging.getLogger(__name__)


class Client(CommandLineApplication):
    """Send and receives messages to and from the server."""

    def __init__(self, arguments: list[str]) -> None:
        """Initialise the client with specified arguments.

        :param arguments: A list containing the host name, port number,
        username, and message type.
        """
        super().__init__(
            OrderedDict(
                host_name=parse_hostname,
                port_number=PortNumber,
                user_name=parse_username,
                message_type=MessageType.from_str,
            ),
        )

        parsed_arguments: tuple[str, PortNumber, str, MessageType]
        parsed_arguments = self.parse_arguments(arguments)

        self.host_name, self.port_number, self.user_name, self.message_type = (
            parsed_arguments
        )

        logger.debug(
            "Client for %s port %s created by %s to send %s request",
            self.host_name,
            self.port_number,
            self.user_name,
            self.message_type.name.lower(),
        )

        self.public_key, self.__private_key = rsa.newkeys(512)

        logger.debug(
            "Created key %s for user %s",
            (self.public_key.n, self.public_key.e),
            self.user_name,
        )

        self.session_token: bytes | None = None
        self.key_cache: dict[str, rsa.PublicKey] = {}

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
            raise SystemExit from error

        logger.info(
            "%s record sent as %s",
            self.message_type.name.capitalize(),
            self.user_name,
        )

        return response

    def send_registration_request(self) -> None:
        """Send a registration request to the server."""
        request = RegistrationRequest(self.user_name, self.public_key)
        self.send_request(request, expect_response=False)

    def send_login_request(self) -> bytes:
        """Send a login request to the server.

        :raises RuntimeError: If the server sends an incorrect response.
        :return: The LoginResponse packet from the server.
        """
        request = LoginRequest(self.user_name)
        response = self.send_request(request)

        message_type: MessageType
        packet: bytes
        message_type, _, packet = Packet.decode_packet(response)
        if message_type != MessageType.LOGIN_RESPONSE:
            raise RuntimeError("Recieved incorrect type response from server")

        (encrypted_session_token,) = LoginResponse.decode_packet(packet)
        logger.debug("Received encrypted token bytes %s", encrypted_session_token)

        if len(encrypted_session_token) == 0:
            logger.error("You are not registered! Please register before logging in")
            raise SystemExit

        self.session_token = rsa.decrypt(encrypted_session_token, self.__private_key)
        logger.debug("Storing provided session token %s", self.session_token)
        logger.info("Now logged in as %s", self.user_name)

        return packet

    def send_key_request(self, receiver_name: str | None = None) -> bytes:
        """Send a pubblic key request to the server.

        :param receiver_name: The name of the user who's key should be requested.
        :return: The KeyResponse packet from the server.
        """
        if not receiver_name:
            receiver_name = input("Who's key are we requesting? ")

        request = KeyRequest(receiver_name)
        response = self.send_request(request)

        message_type: MessageType
        packet: bytes
        message_type, _, packet = Packet.decode_packet(response)

        if message_type != MessageType.KEY_RESPONSE:
            logger.error("Recieved incorrect type response from server")
            raise SystemExit

        (public_key,) = KeyResponse.decode_packet(packet)

        if public_key is None:
            logger.warning("The requested user is not registered")
        else:
            logger.info(
                "Received %s's key:\n%s",
                receiver_name,
                (public_key.n, public_key.e),
            )

        return packet

    def send_create_request(
        self,
        receiver_name: str | None = None,
        message: str | None = None,
    ) -> None:
        """Send a create request to the server.

        :param receiver_name: The name of the person to send the messag to.
        :param message: The message to be sent.
        """
        if self.session_token is None:
            logger.error("Please log in before sending messages")
            raise SystemExit

        if receiver_name is None:
            receiver_name = input("Enter the name of the receiver: ")

        if message is None:
            message = input("Enter the message to be sent: ")

        logger.debug(
            'User specified message to %s: "%s"',
            receiver_name,
            message,
        )

        # encrypted_message = rsa.encrypt(message.encode(),
        # self.key_cache[receiver_name])

        request = CreateRequest(
            self.session_token,
            receiver_name,
            message,
        )
        self.send_request(request, expect_response=False)

    @staticmethod
    def read_message_response(packet: bytes) -> None:
        """Read a message response from the server.

        :param packet: The message response from the server.
        """
        messages, more_messages = ReadResponse.decode_packet(packet)

        for sender, message in messages:
            logger.info("\nMessage from %s:\n%s", sender, message)

        if len(messages) == 0:
            logger.info("No messages available")
        elif more_messages:
            logger.info("More messages available, please send another request")

    def send_read_request(self) -> bytes:
        """Send a read request to the server.

        :raises RuntimeError: If the server sends an invalid response.
        :return: The ReadResponse packet received from the server.
        """
        if self.session_token is None:
            logger.error("Please log in to request messages")
            raise SystemExit

        request = ReadRequest(self.session_token, self.user_name)
        response = self.send_request(request)

        message_type: MessageType
        packet: bytes
        message_type, _, packet = Packet.decode_packet(response)

        if message_type != MessageType.READ_RESPONSE:
            raise RuntimeError("Incorrect type message recieved from the server.")

        self.read_message_response(packet)
        return packet

    def run(self) -> None:
        """Ask the user to input message and send request to server.

        :param receiver_name: The name of the user to send the message to.
        Will request from ``stdin`` if not present. Defaults to ``None``.
        :param message: The message to send. Will request from
        ``stdin`` if not present. Defaults to ``None``.
        """
        if self.message_type not in SEND_REQUEST_MAPPING:
            logging.error("Given message type is not a valid request!")
            return

        send_function = SEND_REQUEST_MAPPING[self.message_type]
        send_function(self)


ClientSendFunction: TypeAlias = Callable[[Client], bytes | None]
SEND_REQUEST_MAPPING: Final[Mapping[MessageType, ClientSendFunction]] = {
    MessageType.REGISTER: Client.send_registration_request,
    MessageType.LOGIN: Client.send_login_request,
    MessageType.KEY: Client.send_key_request,
    MessageType.CREATE: Client.send_create_request,
    MessageType.READ: Client.send_read_request,
}
