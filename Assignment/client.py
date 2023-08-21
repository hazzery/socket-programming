"""
Client side program for COSC264 socket programming assignment

Harrison Parkes (hpa101) 94852440
"""
import socket
import sys

from common import *

USAGE_PROMPT = "Usage: python3 client.py <host_name> <port_number> <user_name> <message_type>"


def parse_arguments() -> tuple[str, int, str, MessageType]:
    """
    Parses the command line arguments, ensuring they are valid.
    :return: A tuple containing the host name, port number, username, and message type
    """
    if len(sys.argv) != 5:
        print(USAGE_PROMPT)
        sys.exit(1)

    if not sys.argv[2].isdigit():
        print(USAGE_PROMPT)
        print("Port number must be an integer")
        sys.exit(1)

    port_number = int(sys.argv[2])

    if not 1024 <= port_number <= 64000:
        print(USAGE_PROMPT)
        print("Port number must be between 1024 and 64000 (inclusive)")
        sys.exit(1)

    host_name = sys.argv[1]

    try:
        socket.getaddrinfo(host_name, port_number)
    except socket.gaierror:
        print(USAGE_PROMPT)
        print("Invalid host name")
        sys.exit(1)

    user_name = sys.argv[3]
    if len(user_name.encode()) > 255:
        print(USAGE_PROMPT)
        print("Username must be at most 255 bytes")
        sys.exit(1)

    try:
        message_type = MessageType[sys.argv[4].upper()]
    except KeyError:
        print(USAGE_PROMPT)
        print("Invalid message type, must be \"read\" or \"create\"")
        sys.exit(1)

    if message_type == MessageType.RESPONSE:
        print(USAGE_PROMPT)
        print("Message type \"response\" not allowed, must be \"read\" or \"create\"")
        sys.exit(1)

    return host_name, port_number, user_name, message_type


def create_message_request(message_type: MessageType, user_name: str) -> bytes:
    """
    Creates a message request packet
    :param message_type: The type of the request (READ or CREATE)
    :param user_name: The name of the user sending the request
    :return: A message request packet as an array of bytes
    """
    receiver_name = ""
    message = ""
    if message_type == MessageType.CREATE:
        receiver_name = input("Enter the name of the message recipient: ")
        while not 1 <= len(receiver_name.encode()) <= 255:
            receiver_name = input("recipient name must be between 1 and 255 characters")

        message = input("Enter the message to be sent: ")
        while not 1 <= len(message.encode()) <= 65535:
            message = input("message must be between 1 and 65535 characters")

    record = bytearray(7)
    record[0] = MESSAGE_MAGIC_NUMBER >> 8
    record[1] = MESSAGE_MAGIC_NUMBER & 0xFF
    record[2] = message_type.value
    record[3] = len(user_name.encode())
    record[4] = len(receiver_name.encode())
    record[5] = len(message.encode()) >> 8
    record[6] = len(message.encode()) & 0xFF

    record.extend(user_name.encode())
    record.extend(receiver_name.encode())
    record.extend(message.encode())

    return record


def decode_messages(num_messages: int, record: bytes) -> list[tuple[str, str]]:
    """
    Decode a singular message from a message response packet
    :param num_messages: The number of messages to be decoded
    :param record: An array of bytes containing the messages to be decoded
    :return: A list of tuples containing the sender name and message
    """
    messages: list = [None] * num_messages

    index = 0
    for i in range(num_messages):
        sender_name_length = record[index]
        index += 1

        message_length = (record[index] << 8) | record[index + 1] & 0xFF
        index += 2

        sender_name = record[index:index + sender_name_length].decode()
        index += sender_name_length

        message = record[index:index + message_length].decode()
        index += message_length

        messages[i] = (sender_name, message)

    return messages


def decode_message_response(record: bytes) -> tuple[list[tuple[str, str]], bool]:
    """
    Decodes a message response packet
    :param record: The packet to be decoded
    :return: A tuple containing the message type, sender name, and message
    """
    magic_number = record[0] << 8 | record[1]
    if magic_number != MESSAGE_MAGIC_NUMBER:
        raise ValueError("Invalid magic number when decoding message response")

    try:
        message_type = MessageType(record[2])
    except ValueError:
        raise ValueError("Invalid message type when decoding message response")
    if message_type != MessageType.RESPONSE:
        raise ValueError(f"Message type {message_type} found when decoding message response, "
                         f"expected RESPONSE")

    num_messages = record[3]
    more_messages = bool(record[4])

    messages = decode_messages(num_messages, record[5:])

    return messages, more_messages


def open_socket(host_name: str, port_number: int) -> socket.socket:
    """
    Opens a socket to the server
    :param host_name: The IP address of the server
    :param port_number: The port number the server is listening on
    :return: A socket connected to the server
    """
    connection_socket = socket.socket()
    connection_socket.settimeout(1)

    try:
        connection_socket.connect((host_name, port_number))
    except ConnectionRefusedError:
        print("Connection refused by server, likely due to invalid port number")
        connection_socket.close()
        sys.exit(1)
    except socket.timeout:
        print("Connection timed out, likely due to invalid host name")
        connection_socket.close()
        sys.exit(1)

    return connection_socket


def send_message_request(record: bytes, connection_socket: socket.socket,
                         message_type: MessageType, user_name: str):
    """
    Sends a message request record to the server
    :param record: The message request packet to be sent
    :param connection_socket: The socket to send the packet over
    :param message_type: The type of message request being sent
    :param user_name: The name of the user sending the request
    """
    try:
        connection_socket.send(record)
    except socket.timeout:
        print("Connection timed out while sending message to server")
        connection_socket.close()
        sys.exit(1)

    print(f"{message_type.name.lower()} record sent as {user_name}")


def read_message_response(connection_socket: socket.socket):
    """
    Reads a message response from the server
    :param connection_socket: The socket to read the response from
    :return:
    """
    response = connection_socket.recv(4096)
    print("Received response from server\n")
    try:
        messages, more_messages = decode_message_response(response)
    except ValueError as error:
        print(error)
        connection_socket.close()
        sys.exit(1)

    for sender, message in messages:
        print(f"Message from {sender}:\n{message}\n")

    if len(messages) == 0:
        print("No messages available")
    elif more_messages:
        print("More messages available, please send another request")


def main():
    """
    Defines the main flow of the client program
    """
    host_name, port_number, user_name, message_type = parse_arguments()
    record = create_message_request(message_type, user_name)
    connection_socket = open_socket(host_name, port_number)
    send_message_request(record, connection_socket, message_type, user_name)
    if message_type == MessageType.READ:
        read_message_response(connection_socket)

    connection_socket.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
