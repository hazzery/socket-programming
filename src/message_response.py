"""
This module contains the MessageResponse class, which is used to encode and decode
message response packets.
"""

from typing import Union
import logging
from typing import Union

from .message_type import MessageType
from .record import Record


class MessageResponse(Record):
    """
    A class for encoding and decoding message response packets
    """

    def __init__(self, messages: list[tuple[str, Union[str, bytes]]]):
        """
        Encodes a record containing all (up to 255) messages for the specified sender
        :param messages: A list of all the messages to be put in the record
        """
        self.num_messages = min(len(messages), 255)
        self.more_messages = len(messages) > 255

        self.messages = messages[:self.num_messages]
        self.record = bytearray(5)

    def to_bytes(self) -> bytes:
        """
        Returns the message response packet
        :return: A byte array holding the message response
        """
        logging.info("Creating message response for %s message(s)", self.num_messages)

        self.record[0] = Record.MAGIC_NUMBER >> 8
        self.record[1] = Record.MAGIC_NUMBER & 0xFF
        self.record[2] = MessageType.RESPONSE.value
        self.record[3] = self.num_messages
        self.record[4] = int(self.more_messages)

        for sender, message in self.messages:
            self.record.append(len(sender.encode()))
            self.record.append(len(message) >> 8)
            self.record.append(len(message) & 0xFF)
            self.record.extend(sender.encode())
            self.record.extend(message)
            logging.info("Encoded message from %s: \"%s\"", sender, message.decode())

        return bytes(self.record)

    @classmethod
    def from_record(cls, record: bytes) -> "MessageResponse":
        """
        Decodes a message response packet
        :param record: The packet to be decoded
        """
        magic_number = record[0] << 8 | record[1]
        if magic_number != Record.MAGIC_NUMBER:
            raise ValueError("Invalid magic number when decoding message response")

        try:
            message_type = MessageType(record[2])
        except ValueError as error:
            raise ValueError("Invalid message type when decoding message response") from error
        if message_type != MessageType.RESPONSE:
            raise ValueError(f"Message type {message_type} found when decoding message response, "
                             f"expected RESPONSE")

        num_messages = record[3]
        messages: list[tuple[str, str]] = []

        index = 5
        for _ in range(num_messages):
            sender_name_length = record[index]
            index += 1

            message_length = (record[index] << 8) | (record[index + 1] & 0xFF)
            index += 2

            sender_name = record[index:index + sender_name_length].decode()
            index += sender_name_length

            message = record[index:index + message_length].decode()
            index += message_length

            logging.info("Decoded message from %s: \"%s\"", sender_name, message)
            messages.append((sender_name, message))

        response = cls(messages)
        response.more_messages = bool(record[4])

        return response

    def decode(self) -> tuple[list[tuple[str, str]], bool]:
        """
        Decodes the message response packet
        :return: A tuple containing a list of messages and a boolean
            indicating whether there are more messages to be received
        """
        return self.messages, self.more_messages
