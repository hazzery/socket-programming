"""Home to the ``MessageResponse`` class."""

import logging
import struct

from src.message_type import MessageType
from src.packets.message import Message
from src.packets.packet import Packet

logger = logging.getLogger(__name__)


class MessageResponse(Packet, struct_format="!HBB?"):
    """Enables encoding and decoding message response packets."""

    MAX_MESSAGE_LENGTH = 255

    def __init__(self, messages: list[tuple[str, bytes]]) -> None:
        """Encode a structure containing up to 255 messages for a specific sender.

        :param messages: A list of all the messages to be put in the structure.
        """
        self.num_messages = min(len(messages), MessageResponse.MAX_MESSAGE_LENGTH)
        self.more_messages = len(messages) > MessageResponse.MAX_MESSAGE_LENGTH

        self.messages = messages[: self.num_messages]
        self.packet = b""

    def to_bytes(self) -> bytes:
        """Return the message response packet.

        :return: A byte array holding the message response.
        """
        logger.info("Creating message response for %s message(s)", self.num_messages)

        self.packet = struct.pack(
            self.struct_format,
            Packet.MAGIC_NUMBER,
            MessageType.RESPONSE.value,
            self.num_messages,
            self.more_messages,
        )

        for sender, message in self.messages:
            self.packet += Message(sender, message).to_bytes()
            logger.info('Encoded message from %s: "%s"', sender, message.decode())

        return self.packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[list[tuple[str, str]], bool]:
        """Decode a message response packet into its individual components.

        :param packet: The packet to be decoded.
        :return: A tuple containing a list of messages and a boolean
            indicating whether there are more messages to be received.
        """
        header_fields, payload = cls.split_packet(packet)
        magic_number, message_type, num_messages, more_messages = header_fields

        if magic_number != Packet.MAGIC_NUMBER:
            raise ValueError("Invalid magic number when decoding message response")

        try:
            message_type = MessageType(message_type)
        except ValueError as error:
            raise ValueError(
                "Invalid message type when decoding message response",
            ) from error
        if message_type != MessageType.RESPONSE:
            message = (
                f"Message type {message_type} found when decoding message"
                " response, expected RESPONSE"
            )
            raise ValueError(message)

        messages: list[tuple[str, str]] = []
        remaining_messages = payload
        for _ in range(num_messages):
            sender_name, message, remaining_messages = Message.decode_packet(
                remaining_messages,
            )
            logger.info('Decoded message from %s: "%s"', sender_name, message)
            messages.append((sender_name, message))

        return messages, more_messages
