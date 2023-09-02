"""
Server side program
Run with `python3 server.py <port number>`
"""
from collections import OrderedDict
from datetime import datetime
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
        """
        Initialises the server with a specified port number.
        """
        super().__init__(OrderedDict(port_number=PortNumber))
        self.port_number, = self.parse_arguments(arguments)

        self.server_address = ("localhost", self.port_number)
        self.messages: dict[str, list[tuple[str, bytes]]] = dict()

    def run(self):
        try:
            # Create a TCP/IP socket
            with socket.socket() as welcoming_socket:
                welcoming_socket.bind(self.server_address)  # Bind the socket to the port
                welcoming_socket.listen(5)  # A maximum, of five unprocessed connections are allowed
                logging.info("Server started on %s port %s" % self.server_address)
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

        logging.info(f"New client connection from {client_address}")
        print("New client connection from", client_address)

        try:
            with connection_socket:
                record = connection_socket.recv(4096)
                request = MessageRequest.from_record(record)
                message_type, sender_name, receiver_name, message = request.decode()

                if message_type == MessageType.READ:
                    response = MessageResponse(self.messages.get(sender_name, []))
                    record = response.to_bytes()
                    connection_socket.send(record)
                    del self.messages.get(sender_name, [])[:response.num_messages]
                    logging.info(f"{response.num_messages} message(s) delivered to {sender_name}")
                    print(f"{response.num_messages} message(s) delivered to {sender_name}")

                elif message_type == MessageType.CREATE:
                    if receiver_name not in self.messages:
                        self.messages[receiver_name] = []

                    self.messages[receiver_name].append((sender_name, message))
                    logging.info(f"Storing {sender_name}'s message to {receiver_name}:"
                                 f" \"{message.decode()}\"")
                    print(f"{sender_name} sends the message "
                          f"\"{message.decode()}\" to {receiver_name}")

        except socket.timeout as error:
            logging.error(error)
            print("Timed out while waiting for message request")
        except ValueError as error:
            logging.error(error)
            print("Message request discarded")


def main():
    logging.basicConfig(level=logging.INFO,
                        filename=f"logs/server/{datetime.now()}.log",
                        format='%(asctime)s - %(levelname)s: %(message)s',
                        datefmt='%H:%M:%S')
    try:
        server = Server(sys.argv[1:])
        server.run()
    except SystemExit:
        sys.exit(1)
    except KeyboardInterrupt:
        print("Server shut down")
        sys.exit(0)


if __name__ == "__main__":
    main()
