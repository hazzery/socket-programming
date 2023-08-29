"""
Client side program for COSC264 socket programming assignment

Harrison Parkes (hpa101) 94852440
"""
from collections import OrderedDict
from typing import Optional
import socket
import sys

from .command_line_application import CommandLineApplication
from .message_response import MessageResponse
from .message_request import MessageRequest
from .message_type import MessageType
from .port_number import PortNumber


class Client(CommandLineApplication):

    def __init__(self, arguments: list[str]):
        super().__init__(OrderedDict(host_name=str,
                                     port_number=PortNumber,
                                     user_name=str,
                                     message_type=MessageType))
        try:
            self.host_name, self.port_number, self.user_name, self.message_type \
                = self.parse_arguments(arguments)
        except (TypeError, ValueError) as error:
            raise error

        self.receiver_name = None
        self.message = None

    def parse_arguments(self, arguments: list[str]) -> tuple[str, PortNumber, str, MessageType]:
        """
        Parses the command line arguments, ensuring they are valid.
        :param arguments: The command line arguments as a list of strings
        :return: A tuple containing the host name, port number, username, and message type
        """

        host_name, port_number, user_name, message_type = super().parse_arguments(arguments)

        try:
            socket.getaddrinfo(host_name, port_number)
        except socket.gaierror as error:
            # log error
            print(self.usage_prompt)
            raise ValueError("Invalid host name")

        if len(user_name.encode()) > 255:
            print(self.usage_prompt)
            raise ValueError("Username must be at most 255 bytes")

        if message_type == MessageType.RESPONSE:
            print(self.usage_prompt)
            raise ValueError(
                "Message type \"response\" not allowed, must be \"read\" or \"create\"")

        return host_name, port_number, user_name, message_type

    def send_message_request(self, request: MessageRequest) -> Optional[MessageResponse]:
        """
        Sends a message request record to the server
        :param request: The message request to be sent
        """
        record = request.to_bytes()
        response = None
        try:
            with socket.socket() as connection_socket:
                connection_socket.settimeout(1)
                connection_socket.connect((self.host_name, self.port_number))
                connection_socket.send(record)
                if self.message_type == MessageType.CREATE:
                    response = connection_socket.recv(4096)
                    response = MessageResponse(response)

        except ConnectionRefusedError as error:
            # log error
            print("Connection refused by server, likely due to invalid port number")
            raise error
        except socket.timeout as error:
            # log error
            print("Connection timed out, likely due to invalid host name")
            raise error

        print(f"{self.message_type.name.lower()} record sent as {self.user_name}")
        return response

    @staticmethod
    def read_message_response(response: MessageResponse):
        """
        Reads a message response from the server
        :param response: The message response from the server
        """
        messages, more_messages = response.decode()

        for sender, message in messages:
            print(f"Message from {sender}:\n{message}\n")

        if len(messages) == 0:
            print("No messages available")
        elif more_messages:
            print("More messages available, please send another request")

    def run(self):
        request = MessageRequest(self.message_type, self.user_name,
                                 self.receiver_name, self.message)
        response = self.send_message_request(request)
        if self.message_type == MessageType.READ:
            self.read_message_response(response)


if __name__ == '__main__':
    client = Client(sys.argv[1:])
    client.run()
