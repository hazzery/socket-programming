"""
Message request module
This module contains the MessageRequest class which is used to encode and decode
message request packets.
"""

import logging
from typing import Union

from .message_type import MessageType
from .record import Record


class MessageRequest(Record):
    """
    The MessageRequest class is used to encode and decode message request packets.

    Usage:
        message_request = MessageRequest(MessageType.CREATE, "sender_name", "receiver_name", "Hi")
        record = message_request.to_bytes()

        message_request = MessageRequest.from_record(record)
        message_type, sender_name, receiver_name, message = message_request.decode()
    """

    def __init__(self, message_type: MessageType, user_name: str,
                 receiver_name: str, message: Union[str, bytes]):
        """
        Encodes a message request packet
        :param message_type: The type of the request (READ or CREATE)
        :param user_name: The name of the user sending the request
        :param receiver_name: The name of the message recipient
        :param message: The string message to be sent
        """
        self.message_type = message_type
        self.user_name = user_name
        self.receiver_name = receiver_name
        self.message = message
        self.record = bytearray(7)

    def to_bytes(self) -> bytes:
        """
        Returns the message request packet
        :return: A byte array holding the message request
        """
        if self.message_type == MessageType.READ:
            logging.info("Creating READ request from %s", self.user_name)
        else:
            logging.info("Creating CREATE request to send %s the message \"%s\" from %s",
                         self.receiver_name, self.message, self.user_name)

        self.record[0] = Record.MAGIC_NUMBER >> 8
        self.record[1] = Record.MAGIC_NUMBER & 0xFF
        self.record[2] = self.message_type.value
        self.record[3] = len(self.user_name.encode())
        self.record[4] = len(self.receiver_name.encode())
        self.record[5] = len(self.message.encode()) >> 8
        self.record[6] = len(self.message.encode()) & 0xFF

        self.record.extend(self.user_name.encode())
        self.record.extend(self.receiver_name.encode())
        self.record.extend(self.message.encode())

        return bytes(self.record)

    @classmethod
    def from_record(cls, record: bytes) -> "MessageRequest":
        """
        Decodes a message request packet
        :param record: An array of bytes containing the message request
        """
        magic_number = record[0] << 8 | record[1]
        if magic_number != Record.MAGIC_NUMBER:
            raise ValueError("Received message request with incorrect magic number")

        if 1 <= record[2] <= 2:
            message_type = MessageType(record[2])
        else:
            raise ValueError("Received message request with invalid ID")

        user_name_length = record[3]
        receiver_name_length = record[4]
        message_length = record[5] << 8 | record[6]

        if user_name_length < 1:
            raise ValueError("Received message request with insufficient user name length")

        if message_type == MessageType.READ:
            if receiver_name_length != 0:
                raise ValueError("Received read request with non-zero receiver name length")
            if message_length != 0:
                raise ValueError("Received read request with non-zero message length")

        elif message_type == MessageType.CREATE:
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

        return cls(message_type, user_name, receiver_name, message)

    def decode(self) -> tuple[MessageType, str, str, bytes]:
        """
        Decodes the message request packet
        :return: A tuple containing the message type, username, receiver name and message
        """
        return self.message_type, self.user_name, self.receiver_name, self.message
