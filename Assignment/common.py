"""
Common functionality to both the server and client side programs
for COSC264 socket programming assignment

Harrison Parkes (hpa101) 94852440
"""
from enum import Enum

MESSAGE_MAGIC_NUMBER = 0xAE73


class MessageType(Enum):
    READ = 1
    CREATE = 2
    RESPONSE = 3


def parse_port_number(port_number: str) -> int:
    """
    Checks that the provided port number is valid
    :param port_number: A string containing the port number
    :return: The port number as an integer
    """
    if not port_number.isdigit():
        raise TypeError("Port number must be an integer")

    port_number = int(port_number)

    if not 1024 <= port_number <= 64000:
        raise ValueError("Port number must be between 1024 and 64000 (inclusive)")

    return port_number
