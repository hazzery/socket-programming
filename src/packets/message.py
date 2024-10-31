"""Home to the ``Message`` class."""

import struct

from .packet import Packet


class Message(Packet, struct_format="!BH"):
    """A class for encoding and decoding message packets.

    Message "packets" are the encoding of a single message from within
    a MessageResponse packet.
    """

    def __init__(self, sender_name: str, message: bytes) -> None:
        """Create the Message which can be encoded into a packet.

        :param sender_name: The name of the user sending this message.
        :param message: The message to be sent.
        """
        self.sender_name = sender_name
        self.message = message
        self.packet = b""

    def to_bytes(self) -> bytes:
        """Encode the message into bytes for transmission through a socket.

        :return: A ``bytes`` object encoding the message.
        """
        self.packet += struct.pack(
            self.struct_format,
            len(self.sender_name.encode()),
            len(self.message),
        )
        self.packet += self.sender_name.encode()
        self.packet += self.message

        return self.packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[str, str, bytes]:
        """Decode a message packet into it's sender name and message.

        :param packet: A ``bytes`` object containing the message to be decoded.
        :return: The sender name and message,
            as well as all remaining bytes for other potential messages.
        """
        header_fields, payload = cls.split_packet(packet)
        sender_name_length, message_length = header_fields

        sender_name = payload[:sender_name_length].decode()
        index = sender_name_length

        message = payload[index : index + message_length].decode()
        index += message_length

        remaining_messages = payload[index:]

        return sender_name, message, remaining_messages
