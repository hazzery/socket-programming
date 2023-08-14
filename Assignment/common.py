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
