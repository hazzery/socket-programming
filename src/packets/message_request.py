"""
Message request module
This module contains the MessageRequest class which is used to encode and decode
message request packets.
"""

import logging
import struct

from src.message_type import MessageType
from .packet import Packet


class MessageRequest(Packet, struct_format="!HBBBH"):
    """
    The MessageRequest class is used to encode and decode message request packets.

    Usage:
        message_request = MessageRequest(MessageType.CREATE, "sender_name", "receiver_name", "Hi")
        record = message_request.to_bytes()

        message_request = MessageRequest.from_record(record)
        message_type, sender_name, receiver_name, message = message_request.decode()
    """

    def __init__(self, message_type: MessageType, user_name: str,
                 receiver_name: str, message: str):
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
        self.packet = bytes()

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

        self.packet = struct.pack(self.struct_format,
                                  Packet.MAGIC_NUMBER,
                                  self.message_type.value,
                                  len(self.user_name.encode()),
                                  len(self.receiver_name.encode()),
                                  len(self.message.encode()))

        self.packet += self.user_name.encode()
        self.packet += self.receiver_name.encode()
        self.packet += self.message.encode()

        return self.packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[MessageType, str, str, bytes]:
        """
        Decodes a message request packet
        :param packet: An array of bytes containing the message request
        """
        header_fields, payload = cls.split_packet(packet)
        magic_number, message_type, user_name_size, receiver_name_size, message_size = header_fields

        if magic_number != Packet.MAGIC_NUMBER:
            raise ValueError("Received message request with incorrect magic number")

        if 1 <= message_type <= 2:
            message_type = MessageType(message_type)
        else:
            raise ValueError("Received message request with invalid ID")

        if user_name_size < 1:
            raise ValueError("Received message request with insufficient user name length")

        if message_type == MessageType.READ:
            if receiver_name_size != 0:
                raise ValueError("Received read request with non-zero receiver name length")
            if message_size != 0:
                raise ValueError("Received read request with non-zero message length")

        elif message_type == MessageType.CREATE:
            if receiver_name_size < 1:
                raise ValueError("Received create request with insufficient receiver name length")
            if message_size < 1:
                raise ValueError("Received create request with insufficient message length")

        user_name = payload[:user_name_size].decode()
        index = user_name_size

        receiver_name = payload[index:index + receiver_name_size].decode()
        index += receiver_name_size

        message = payload[index:index + message_size]

        return message_type, user_name, receiver_name, message
