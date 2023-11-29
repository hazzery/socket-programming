"""
The client module contains the Client class
"""
from collections import OrderedDict
from typing import Optional
import logging
import socket

from src.applications.command_line_application import CommandLineApplication
from src.packets.message_response import MessageResponse
from src.packets.message_request import MessageRequest
from src.message_type import MessageType
from src.port_number import PortNumber


logger = logging.getLogger(__name__)


class Client(CommandLineApplication):
    """
    A client side program that sends and receives messages to and from the server.
    """

    def __init__(self, arguments: list[str]):
        """
        Initialises the client with a specified host name, port number, username, and message type.
        """
        super().__init__(
            OrderedDict(
                host_name=self.parse_hostname,
                port_number=PortNumber,
                user_name=self.parse_username,
                message_type=MessageType.from_str,
            )
        )

        # pylint thinks that self.parse_arguments is only capable of returning an empty list
        # pylint: disable=unbalanced-tuple-unpacking
        (
            self.host_name,
            self.port_number,
            self.user_name,
            self.message_type,
        ) = self.parse_arguments(arguments)

        logger.info(
            "Client for %s port %s created by %s to send %s request",
            self.host_name,
            self.port_number,
            self.user_name,
            self.message_type.name.lower(),
        )

        self.receiver_name = ""
        self.message = ""

    @staticmethod
    def parse_hostname(host_name: str) -> str:
        """
        Parses the host name, ensuring it is valid.
        :param host_name: String representing the host name
        :return: String of the host name
        :raises ValueError: If the host name is invalid
        """
        try:
            socket.getaddrinfo(host_name, 1024)
        except socket.gaierror as error:
            logger.error(error)
            raise ValueError(
                "Invalid host name, must be an IP address, domain name,"
                ' or "localhost"'
            ) from error

        return host_name

    @staticmethod
    def parse_username(user_name: str) -> str:
        """
        Parses the username, ensuring it is valid.
        :param user_name: String representing the username
        :return: String of the username
        :raises ValueError: If the username is invalid
        """
        if len(user_name) == 0:
            logger.error("Username is empty")
            raise ValueError("Username must not be empty")

        if len(user_name.encode()) > 255:
            logger.error("Username consumes more than 255 bytes")
            raise ValueError("Username must consume at most 255 bytes")

        return user_name

    def send_message_request(self, request: MessageRequest) -> Optional[bytes]:
        """
        Sends a message request record to the server
        :param request: The message request to be sent
        :return: The server's response if applicable, otherwise ``None``
        """
        packet = request.to_bytes()
        response = None
        try:
            with socket.socket() as connection_socket:
                connection_socket.settimeout(1)
                connection_socket.connect((self.host_name, self.port_number))
                connection_socket.send(packet)
                if self.message_type == MessageType.READ:
                    response = connection_socket.recv(4096)

        except ConnectionRefusedError as error:
            logger.error(error)
            print("Connection refused, likely due to invalid port number")
            raise SystemExit from error
        except socket.timeout as error:
            logger.error(error)
            print("Connection timed out, likely due to invalid host name")
            raise SystemExit from error

        logger.info(
            "%s record sent as %s", self.message_type.name.lower(), self.user_name
        )
        print(f"{self.message_type.name.lower()} record sent as {self.user_name}")

        return response

    @staticmethod
    def read_message_response(packet: bytes) -> None:
        """
        Reads a message response from the server
        :param packet: The message response from the server
        """
        messages, more_messages = MessageResponse.decode_packet(packet)

        for sender, message in messages:
            logger.info('Received %s\'s message "%s"', sender, message)
            print(f"Message from {sender}:\n{message}\n")

        if len(messages) == 0:
            logger.info("Response contained no messages")
            print("No messages available")
        elif more_messages:
            logger.info("Server has more messages available for this user")
            print("More messages available, please send another request")

    def run(self) -> None:
        if self.message_type == MessageType.CREATE:
            self.receiver_name = input("Enter the name of the receiver: ")
            self.message = input("Enter the message to be sent: ")
            logger.info(
                'User specified message to %s: "%s"', self.receiver_name, self.message
            )

        request = MessageRequest(
            self.message_type, self.user_name, self.receiver_name, self.message
        )
        response = self.send_message_request(request)
        if self.message_type == MessageType.READ and response:
            self.read_message_response(response)
