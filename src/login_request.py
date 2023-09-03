"""
Login request module.
Defines the LoginRequest class which is used to encode and decode login request packets.
"""
import logging

from .message_type import MessageType
from .record import Record


class LoginRequest(Record):
    """
    The LoginRequest class is used to encode and decode login request packets.
    """
    def __init__(self, user_name: str):
        """
        Create a login request packet
        """
        self.user_name = user_name
        self.record = bytearray(4)

    def to_bytes(self) -> bytes:
        """
        Encode the login request packet into a byte array
        """
        logging.info("Creating log-in request as %s", self.user_name)

        self.record[0] = Record.MAGIC_NUMBER >> 8
        self.record[1] = Record.MAGIC_NUMBER & 0xFF
        self.record[2] = MessageType.LOGIN.value
        self.record[3] = len(self.user_name.encode())
        self.record.extend(self.user_name.encode())

        return bytes(self.record)

    @classmethod
    def from_record(cls, record: bytes) -> "LoginRequest":
        """
        Create a login request packet from a byte array
        """
        magic_number = record[0] << 8 | record[1]
        if magic_number != Record.MAGIC_NUMBER:
            raise ValueError("Received message request with incorrect magic number")

        if record[2] != MessageType.LOGIN.value:
            raise ValueError("Received log-in request with invalid ID")

        user_name_length = record[3]
        user_name = record[4:4 + user_name_length].decode()

        return cls(user_name)

    def decode(self) -> tuple:
        """
        Decode the individual fields of the login request packet
        :return: A tuple containing the username
        """
        return self.user_name,
