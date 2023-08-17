"""
Client side program for COSC264 socket programming assignment

Harrison Parkes (hpa101) 94852440
"""
import socket
import sys

from common import *

usage_prompt = "Usage: python3 client.py <host_name> <port_number> <user_name> <message_type>"

if len(sys.argv) != 5:
    print(usage_prompt)
    sys.exit(1)

if not sys.argv[2].isdigit():
    print(usage_prompt)
    print("Port number must be an integer")
    sys.exit(1)

port_number = int(sys.argv[2])

if not 1024 <= port_number <= 64000:
    print(usage_prompt)
    print("Port number must be between 1024 and 64000 (inclusive)")
    sys.exit(1)

host_name = sys.argv[1]

try:
    socket.getaddrinfo(host_name, port_number)
except socket.gaierror:
    print(usage_prompt)
    print("Invalid host name")
    sys.exit(1)

user_name = sys.argv[3]
if len(user_name.encode()) > 255:
    print(usage_prompt)
    print("Username must be at most 255 bytes")
    sys.exit(1)

try:
    message_type = MessageType[sys.argv[4].upper()]
except KeyError:
    print(usage_prompt)
    print("Invalid message type, must be \"read\" or \"create\"")
    sys.exit(1)

if message_type == MessageType.RESPONSE:
    print(usage_prompt)
    print("Message type \"response\" not allowed, must be \"read\" or \"create\"")
    sys.exit(1)


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


record = create_message_request(message_type, user_name)

connection_socket = socket.socket()
connection_socket.connect((host_name, port_number))
connection_socket.send(record)
print(f"{message_type.name.lower()} record sent as {user_name}")

if message_type == MessageType.READ:
    response = connection_socket.recv(4096)
    print("Received response from server")
    try:
        messages, more_messages = decode_message_response(response)
    except ValueError as error:
        print(error)
        sys.exit(1)
    for sender, message in messages:
        print(f"Message from {sender}:\n{message}\n")
    if len(messages) == 0:
        print("No messages available")
    if more_messages:
        print("More messages available, please send another request")

connection_socket.close()
sys.exit(0)
