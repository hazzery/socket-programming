"""
Server side program for COSC264 socket programming assignment

Harrison Parkes (hpa101) 94852440
"""
import socket
import sys

from common import *

USAGE_PROMPT = "Usage: python3 server.py <port_number>"


def parse_arguments() -> int:
    """
    Parses the command line arguments, ensuring they are valid.
    :return: The port number
    """
    if len(sys.argv) != 2:
        print(USAGE_PROMPT)
        sys.exit(1)

    _, port_number = sys.argv

    try:
        port_number = parse_port_number(port_number)
    except (TypeError, ValueError) as error:
        print(USAGE_PROMPT)
        print(error)
        sys.exit(1)

    return port_number


def open_welcoming_socket(port_number: int) -> socket.socket:
    """
    Opens a welcoming socket on the provided port
    :param port_number: The port number to open the socket on
    :return: The welcoming socket
    """
    # Create a TCP/IP socket
    welcoming_socket = socket.socket()

    # Bind the socket to the port
    server_address = ("localhost", port_number)
    print("starting up on %s port %s" % server_address)
    try:
        welcoming_socket.bind(server_address)
    except OSError:
        print("Error binding socket on provided port")
        welcoming_socket.close()
        sys.exit(1)

    # The server listens for incoming connections
    # A maximum of 5 unprocessed connections are allowed
    try:
        welcoming_socket.listen(5)
    except OSError:
        print("Error listening on provided port")
        welcoming_socket.close()
        sys.exit(1)

    return welcoming_socket


def decode_message_request(record: bytes) -> tuple[MessageType, str, str, bytes]:
    """
    Decodes the message request sent by the client
    :param record: A message packet
    :return: The individual fields of the message request
    """
    magic_number = record[0] << 8 | record[1]
    if magic_number != MESSAGE_MAGIC_NUMBER:
        raise ValueError("Received message request with incorrect magic number")

    if 1 <= record[2] <= 2:
        mode = MessageType(record[2])
    else:
        raise ValueError("Received message request with invalid ID")

    user_name_length = record[3]
    receiver_name_length = record[4]
    message_length = record[5] << 8 | record[6]

    if user_name_length < 1:
        raise ValueError("Received message request with insufficient user name length")

    if mode == MessageType.READ:
        if receiver_name_length != 0:
            raise ValueError("Received read request with non-zero receiver name length")
        if message_length != 0:
            raise ValueError("Received read request with non-zero message length")

    elif mode == MessageType.CREATE:
        if receiver_name_length < 1:
            raise ValueError("Received create request with insufficient receiver name length")
        if message_length < 1:
            raise ValueError("Received create request with insufficient message length")

    index = 7

    user_name = record[index:index + user_name_length].decode()
    index += user_name_length

    receiver_name = record[index:index + receiver_name_length].decode()
    index += receiver_name_length

    message = record[index:index + message_length]

    return mode, user_name, receiver_name, message


def create_message_response(receiver_name: str, messages: dict[str, list[tuple[str, bytes]]])\
        -> tuple[bytes, int]:
    """
    Encodes a record containing all (up to 255) messages for the specified sender
    :param messages:
    :param receiver_name: The string name of the client requesting their messages
    :return: A MessageResponse record
    """
    num_messages = len(messages.get(receiver_name, []))
    more_messages = False
    if num_messages > 255:
        more_messages = True
        num_messages = 255

    record = bytearray(5)

    record[0] = MESSAGE_MAGIC_NUMBER >> 8
    record[1] = MESSAGE_MAGIC_NUMBER & 0xFF
    record[2] = MessageType.RESPONSE.value
    record[3] = num_messages
    record[4] = int(more_messages)

    if num_messages > 0:
        for i in range(num_messages):
            sender, message = messages[receiver_name][i]

            record.append(len(sender.encode()))
            record.append(len(message) >> 8)
            record.append(len(message) & 0xFF)
            record.extend(sender.encode())
            record.extend(message)

            print(f"{sender}'s message: \"{message.decode()}\" "
                  f"has been delivered to {receiver_name}")
        del messages[receiver_name][:num_messages]

    return record, num_messages


def run_server(welcoming_socket: socket.socket, messages: dict[str, list[tuple[str, bytes]]]):
    """
    Runs the server side of the program
    :param welcoming_socket: The welcoming socket to accept connections on
    :param messages: A dictionary of messages for each user
    """
    connection_socket, client_address = welcoming_socket.accept()
    connection_socket.settimeout(1)

    print("New client connection from", client_address)

    try:
        record = connection_socket.recv(4096)
    except socket.timeout as error:
        print(error)
        print("Timed out while waiting for message request")
        connection_socket.close()
        return

    try:
        mode, sender_name, receiver_name, message = decode_message_request(record)
    except ValueError as error:
        print(error)
        print("Message request discarded")
        connection_socket.close()
        return

    if mode == MessageType.READ:
        response, num_messages = create_message_response(sender_name, messages)
        connection_socket.send(response)
        connection_socket.close()
        print(f"{num_messages} message(s) delivered to {sender_name}")

    elif mode == MessageType.CREATE:
        if receiver_name not in messages:
            messages[receiver_name] = []

        messages[receiver_name].append((sender_name, message))
        connection_socket.close()
        print(f"{sender_name} sends the message \"{message.decode()}\" to {receiver_name}")


def main():
    port_number = parse_arguments()
    welcoming_socket = open_welcoming_socket(port_number)
    messages: dict[str, list[tuple[str, bytes]]] = dict()
    while True:
        run_server(welcoming_socket, messages)


if __name__ == "__main__":
    main()
