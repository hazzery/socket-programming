"""Home to the ``TypeWrapper`` class."""

import struct

from src.message_type import MessageType
from src.packets.packet import Packet


class TypeWrapper(Packet, struct_format="!HB"):
    """Wrapper class to prepend the message type to packets."""

    MAGIC_NUMBER = 0xAE73

    def __init__(self, message_type: MessageType, payload: Packet) -> None:
        """Initialise the packet.

        :param message_type: The type of the payload packet.
        """
        self.payload = payload
        self.message_type = message_type

    def to_bytes(self) -> bytes:
        """Convert the packet into a ``bytes`` object.

        :return: A ``bytes`` object encoding the packet and it's type.
        """
        packet = struct.pack(
            self.struct_format,
            self.MAGIC_NUMBER,
            self.message_type.value,
        )

        packet += self.payload.to_bytes()

        return packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[MessageType, bytes]:
        """Decode the packet into its type and payload.

        :param packet: The packet to decode.
        :return: A tuple of the message type and payload.
        """
        header_fields: tuple[int, MessageType]
        header_fields, payload = cls.split_packet(packet)
        magic_number, message_type_number = header_fields

        if magic_number != TypeWrapper.MAGIC_NUMBER:
            raise ValueError("Incorrect magic number in packet")

        try:
            message_type = MessageType(message_type_number)
        except ValueError as error:
            raise ValueError("Invalid message type ID number") from error

        return message_type, payload
