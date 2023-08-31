"""
Server side program for COSC264 socket programming assignment

Harrison Parkes (hpa101) 94852440
"""
from collections import OrderedDict
import logging
import socket
import sys

from src.command_line_application import CommandLineApplication
from src.message_response import MessageResponse
from src.message_request import MessageRequest
from src.message_type import MessageType
from src.port_number import PortNumber


class Server(CommandLineApplication):

    def __init__(self, arguments: list[str]):
        super().__init__(OrderedDict(port_number=PortNumber))

        try:
            self.port_number, = self.parse_arguments(arguments)
        except (TypeError, ValueError) as error:
            logging.error(error)
            print(self.usage_prompt)
            print(error)
            raise SystemExit

        self.server_address = ("localhost", self.port_number)
        self.messages: dict[str, list[tuple[str, bytes]]] = dict()

    def parse_arguments(self, arguments: list[str]) -> tuple[PortNumber]:
        """
        Parses the command line arguments, ensuring they are valid.
        :param arguments: The command line arguments as a list of strings
        :return: A tuple containing the port number
        """
        return super().parse_arguments(arguments)

    def run(self):
        try:
            # Create a TCP/IP socket
            with socket.socket() as welcoming_socket:
                welcoming_socket.bind(self.server_address)  # Bind the socket to the port
                welcoming_socket.listen(5)  # A maximum, of five unprocessed connections are allowed
                print("starting up on %s port %s" % self.server_address)

                while True:
                    self.run_server(welcoming_socket)

        except OSError as error:
            logging.error(error)
            print("Error binding socket on provided port")
            raise SystemExit

    def run_server(self, welcoming_socket: socket.socket):
        """
        Runs the server side of the program
        :param welcoming_socket: The welcoming socket to accept connections on
        """
        connection_socket, client_address = welcoming_socket.accept()
        connection_socket.settimeout(1)

        print("New client connection from", client_address)

        try:
            with connection_socket:
                record = connection_socket.recv(4096)
                request = MessageRequest(record)
                message_type, sender_name, receiver_name, message = request.decode()

                if message_type == MessageType.READ:
                    response = MessageResponse(sender_name, self.messages)
                    record = response.to_bytes()
                    connection_socket.send(record)
                    print(f"{response.num_messages} message(s) delivered to {sender_name}")

                elif message_type == MessageType.CREATE:
                    if receiver_name not in self.messages:
                        self.messages[receiver_name] = []

                    self.messages[receiver_name].append((sender_name, message))
                    print(f"{sender_name} sends the message "
                          f"\"{message.decode()}\" to {receiver_name}")

        except socket.timeout as error:
            logging.error(error)
            print("Timed out while waiting for message request")
        except ValueError as error:
            logging.error(error)
            print("Message request discarded")


def main():
    logging.basicConfig(filename="server.log", level=logging.DEBUG)
    try:
        server = Server(sys.argv[1:])
        server.run()
    except SystemExit:
        sys.exit(1)


if __name__ == "__main__":
    main()
