"""
Server side program for COSC264 socket programming assignment

Harrison Parkes (hpa101) 94852440
"""
import socket
import sys

from common import *


MESSAGE_MAGIC_NUMBER = 0xAE73
USAGE_PROMPT = "Usage: python3 server.py <port_number>"

if len(sys.argv) != 2:
    print(USAGE_PROMPT)
    sys.exit(1)

if not sys.argv[1].isdigit():
    print(USAGE_PROMPT)
    print("Port number must be an integer")
    sys.exit(1)

port = int(sys.argv[1])

if not 1024 <= port <= 64000:
    print(USAGE_PROMPT)
    print("Port number must be between 1024 and 64000 (inclusive)")
    sys.exit(1)

# Create a TCP/IP socket
welcoming_socket = socket.socket()

# Bind the socket to the port
server_address = ("localhost", port)
print('starting up on %s port %s' % server_address)
try:
    welcoming_socket.bind(server_address)
except OSError:
    print("Error binding socket on provided port")
    sys.exit(1)

# The server listens for incoming connections
# A maximum of 5 unprocessed connections are allowed
try:
    welcoming_socket.listen(5)
except OSError:
    print("Error listening on provided port")
    sys.exit(1)


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

    user_name = record[7:7 + user_name_length].decode()

    receiver_name = record[7 + user_name_length:7 + user_name_length +
                           receiver_name_length].decode()

    message = record[7 + user_name_length + receiver_name_length:7 + user_name_length +
                     receiver_name_length + message_length]

    return mode, user_name, receiver_name, message


messages: dict[str, list[tuple[str, bytes]]] = dict()


def create_message_response(receiver_name: str) -> tuple[bytes, int]:
    """
    Encodes a record containing all (up to 255) messages for the specified sender
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
    record[2] = int(MessageType.RESPONSE)
    record[3] = num_messages
    record[4] = int(more_messages)

    if num_messages > 0:
        for sender, message in messages[receiver_name]:
            record.append(len(receiver_name.encode()))
            record.append(len(message) >> 8)
            record.append(len(message) & 0xFF)
            record.extend(message)

    return record, num_messages


while True:
    connection_socket, client_address = welcoming_socket.accept()
    connection_socket.settimeout(1)

    print('connection from', client_address)

    try:
        record = connection_socket.recv(4096)
    except socket.timeout as error:
        # print("Timed out while waiting for message request")
        print(error)
        connection_socket.close()
        continue

    try:
        mode, sender_name, receiver_name, message = decode_message_request(record)
    except ValueError as error:
        print(error)
        connection_socket.close()
        continue

    if mode == MessageType.READ:
        response, num_messages = create_message_response(sender_name)
        connection_socket.send(response)
        connection_socket.close()
        print(f"{num_messages} message(s) delivered to {sender_name}")

    elif mode == MessageType.CREATE:
        if receiver_name not in messages:
            messages[receiver_name] = []

        messages[receiver_name].append((sender_name, message))
        connection_socket.close()
        print(f"Message arrived from {sender_name} to {receiver_name}")
