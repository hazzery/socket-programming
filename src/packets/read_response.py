"""Home to the ``CreateResponse`` class."""

import logging
import struct

from src.packets.message import Message
from src.packets.packet import Packet

logger = logging.getLogger(__name__)


class ReadResponse(Packet, struct_format="!B?"):
    """Enables encoding and decoding message response packets."""

    MAX_MESSAGE_LENGTH = 255

    def __init__(self, messages: list[tuple[str, bytes]]) -> None:
        """Encode a structure containing up to 255 messages for a specific sender.

        :param messages: A list of all the messages to be put in the structure.
        """
        self.num_messages = min(len(messages), ReadResponse.MAX_MESSAGE_LENGTH)
        self.more_messages = len(messages) > ReadResponse.MAX_MESSAGE_LENGTH

        self.messages = messages[: self.num_messages]

    def to_bytes(self) -> bytes:
        """Return the message response packet.

        :return: A byte array holding the message response.
        """
        logger.debug("Creating message response for %s message(s)", self.num_messages)

        packet = struct.pack(
            self.struct_format,
            self.num_messages,
            self.more_messages,
        )

        for sender, message in self.messages:
            packet += Message(sender, message).to_bytes()
            logger.info("Encoded message from %s", sender)

        return packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[list[tuple[str, bytes]], bool]:
        """Decode a read response packet into its individual components.

        :param packet: The packet to be decoded.
        :return: A tuple containing a list of messages and a boolean
            indicating whether there are more messages to be received.
        """
        header_fields, payload = cls.split_packet(packet)
        num_messages, more_messages = header_fields

        messages: list[tuple[str, bytes]] = []
        remaining_messages = payload
        for _ in range(num_messages):
            sender_name, encrypted_message, remaining_messages = Message.decode_packet(
                remaining_messages,
            )
            logger.debug("Decoded message from %s", sender_name)
            messages.append((sender_name, encrypted_message))

        return messages, more_messages
