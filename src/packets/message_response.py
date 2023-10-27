"""
This module contains the MessageResponse class, which is used to encode and decode
message response packets.
"""
import logging
import struct

from src.message_type import MessageType
from src.packets.packet import Packet


class MessageResponse(Packet, struct_format="!HBB?"):
    """
    A class for encoding and decoding message response packets
    """

    structure_format = "!HBB?"
    message_structure_format = "!BH"

    def __init__(self, messages: list[tuple[str, bytes]]):
        """
        Encodes a structure containing all (up to 255) messages for the specified sender
        :param messages: A list of all the messages to be put in the structure
        """
        self.num_messages = min(len(messages), 255)
        self.more_messages = len(messages) > 255

        self.messages = messages[:self.num_messages]
        self.packet = bytes()

    def to_bytes(self) -> bytes:
        """
        Returns the message response packet
        :return: A byte array holding the message response
        """
        logging.info("Creating message response for %s message(s)", self.num_messages)

        self.packet = struct.pack(self.structure_format,
                                  Packet.MAGIC_NUMBER,
                                  MessageType.RESPONSE.value,
                                  self.num_messages,
                                  self.more_messages)

        for sender, message in self.messages:
            self.packet += struct.pack(self.message_structure_format,
                                       len(sender.encode()), len(message))
            self.packet += sender.encode()
            self.packet += message
            logging.info("Encoded message from %s: \"%s\"", sender, message.decode())

        return self.packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[list[tuple[str, str]], bool]:
        """
        Decodes a message response packet into its individual components
        :param packet: The packet to be decoded
        :return: A tuple containing a list of messages and a boolean
            indicating whether there are more messages to be received
        """
        structure_size = struct.calcsize(cls.structure_format)
        structure = packet[:structure_size]

        fields = struct.unpack(cls.structure_format, structure)
        magic_number, message_type, num_messages, more_messages = fields

        if magic_number != Packet.MAGIC_NUMBER:
            raise ValueError("Invalid magic number when decoding message response")

        try:
            message_type = MessageType(message_type)
        except ValueError as error:
            raise ValueError("Invalid message type when decoding message response") from error
        if message_type != MessageType.RESPONSE:
            raise ValueError(f"Message type {message_type} found when decoding message response, "
                             "expected RESPONSE")

        messages: list[tuple[str, str]] = []

        index = structure_size
        for _ in range(num_messages):
            structure_size = struct.calcsize(cls.message_structure_format)
            structure = packet[index:index + structure_size]
            sender_name_length, message_length = struct.unpack(cls.message_structure_format,
                                                               structure)
            index += struct.calcsize(cls.message_structure_format)

            sender_name = packet[index:index + sender_name_length].decode()
            index += sender_name_length

            message = packet[index:index + message_length].decode()
            index += message_length

            logging.info("Decoded message from %s: \"%s\"", sender_name, message)
            messages.append((sender_name, message))

        return messages, more_messages
