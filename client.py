"""
Client side program
Run with `python3 client.py <host name> <port number> <username> <message type>`
"""
from collections import OrderedDict
from datetime import datetime
from typing import Optional
import logging
import socket
import sys

from src.command_line_application import CommandLineApplication
from src.message_response import MessageResponse
from src.message_request import MessageRequest
from src.message_type import MessageType
from src.port_number import PortNumber


class Client(CommandLineApplication):

    def __init__(self, arguments: list[str]):
        """
        Initialises the client with a specified host name, port number, username, and message type.
        """
        super().__init__(OrderedDict(host_name=self.parse_hostname,
                                     port_number=PortNumber,
                                     user_name=self.parse_username,
                                     message_type=MessageType.from_str))

        self.host_name, self.port_number, self.user_name, self.message_type =\
            self.parse_arguments(arguments)

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
            logging.error(error)
            raise ValueError("Invalid host name, must be an IP address, domain name,"
                             " or \"localhost\"")

        return host_name

    @staticmethod
    def parse_username(user_name: str) -> str:
        """
        Parses the username, ensuring it is valid.
        :param user_name: String representing the username
        :return: String of the username
        :raises ValueError: If the username is invalid
        """
        if len(user_name.encode()) > 255:
            logging.error("Username consumes more than 255 bytes")
            raise ValueError("Username must consume at most 255 bytes")

        return user_name

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
                if self.message_type == MessageType.READ:
                    response = connection_socket.recv(4096)
                    response = MessageResponse.from_record(response)

        except ConnectionRefusedError as error:
            logging.error(error)
            print("Connection refused, likely due to invalid port number")
            raise SystemExit
        except socket.timeout as error:
            logging.error(error)
            print("Connection timed out, likely due to invalid host name")
            raise SystemExit

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
        if self.message_type == MessageType.CREATE:
            self.receiver_name = input("Enter the name of the receiver: ")
            self.message = input("Enter the message to be sent: ")

        request = MessageRequest(self.message_type, self.user_name,
                                 self.receiver_name, self.message)
        response = self.send_message_request(request)
        if self.message_type == MessageType.READ:
            self.read_message_response(response)


def main():
    logging.basicConfig(filename=f"logs/client/{datetime.now()}.log")
    try:
        client = Client(sys.argv[1:])
        client.run()
    except SystemExit:
        sys.exit(1)


if __name__ == '__main__':
    main()
