from common import *
import socket
import sys

MESSAGE_REQUEST_MAGIC_NUMBER = 0xAE73

if len(sys.argv) != 2:
    print("Usage: python3 server.py <port>")
    sys.exit(1)

if type(sys.argv[1]) != int:
    print("Usage: python3 server.py <port>")
    print("Port must be an integer")
    sys.exit(1)

port = int(sys.argv[1])

if not 1024 <= port <= 64000:
    print("Usage: python3 server.py <port>")
    print("Port must be between 1024 and 64000 (inclusive)")
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


def decode_message_request(record: bytes) -> tuple[MessageType, str, str, str]:
    """
    Decodes the message request sent by the client
    :param record: A message packet
    :return: The individual fields of the message request
    """
    magic_number = record[0] << 8 | record[1]
    if magic_number != MESSAGE_REQUEST_MAGIC_NUMBER:
        raise ValueError("Received message request with incorrect magic number")

    try:
        mode = MessageType(record[2])
    except ValueError:
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
                     receiver_name_length + message_length].decode()

    return mode, user_name, receiver_name, message


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

    if mode == MessageType.

