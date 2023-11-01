"""
The server module contains the Server class
"""
from collections import OrderedDict
import logging
import socket

from src.command_line_application import CommandLineApplication
from src.packets.message_response import MessageResponse
from src.packets.message_request import MessageRequest
from src.message_type import MessageType
from src.port_number import PortNumber


class Server(CommandLineApplication):
    """
    A server side program that receives messages from clients and stores them.

    The server can be run with `python3 server.py <port number>`.
    """

    def __init__(self, arguments: list[str]):
        """
        Initialises the server with a specified port number.
        """
        super().__init__(OrderedDict(port_number=PortNumber))
        # pylint thinks that self.parse_arguments is only capable of returning an empty list
        # pylint: disable=unbalanced-tuple-unpacking
        (self.port_number,) = self.parse_arguments(arguments)

        self.hostname = "localhost"
        self.messages: dict[str, list[tuple[str, bytes]]] = {}

    def run(self) -> None:
        try:
            # Create a TCP/IP socket
            with socket.socket() as welcoming_socket:
                # Bind the socket to the port
                welcoming_socket.bind((self.hostname, self.port_number))
                welcoming_socket.listen(
                    5
                )  # A maximum, of five unprocessed connections are allowed
                logging.info(
                    "Server started on %s port %s", self.hostname, self.port_number
                )
                print(f"starting up on {self.hostname} port {self.port_number}")

                while True:
                    self.run_server(welcoming_socket)

        except OSError as error:
            logging.error(error)
            print("Error binding socket on provided port")
            raise SystemExit from error

    def run_server(self, welcoming_socket: socket.socket) -> None:
        """
        Runs the server side of the program
        :param welcoming_socket: The welcoming socket to accept connections on
        """
        connection_socket, client_address = welcoming_socket.accept()
        connection_socket.settimeout(1)

        logging.info("New client connection from %s", client_address)
        print("New client connection from", client_address)

        try:
            with connection_socket:
                record = connection_socket.recv(4096)
                request_fields = MessageRequest.decode_packet(record)
                message_type, sender_name, receiver_name, message = request_fields

                if message_type == MessageType.READ:
                    response = MessageResponse(self.messages.get(sender_name, []))
                    record = response.to_bytes()
                    connection_socket.send(record)
                    del self.messages.get(sender_name, [])[: response.num_messages]
                    logging.info(
                        "%s message(s) delivered to %s",
                        response.num_messages,
                        sender_name,
                    )
                    print(
                        f"{response.num_messages} message(s) delivered to {sender_name}"
                    )

                elif message_type == MessageType.CREATE:
                    if receiver_name not in self.messages:
                        self.messages[receiver_name] = []

                    self.messages[receiver_name].append((sender_name, message))
                    logging.info(
                        'Storing %s\'s message to %s: "%s"',
                        sender_name,
                        receiver_name,
                        message.decode(),
                    )
                    print(
                        f"{sender_name} sends the message "
                        f'"{message.decode()}" to {receiver_name}'
                    )

        except socket.timeout as error:
            logging.error(error)
            print("Timed out while waiting for message request")
        except ValueError as error:
            logging.error(error)
            print("Message request discarded")
