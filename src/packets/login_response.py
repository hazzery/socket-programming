"""Login response module.

Defines class for encoding and decoding login response packets.
"""

import logging
import struct

from src.message_type import MessageType
from src.packets.packet import Packet


class LoginResponse(Packet, struct_format="!B", message_type=MessageType.LOGIN):
    """The LoginResponse class is used to encode and decode login response packets."""

    def __init__(self, encrypted_token_bytes: bytes) -> None:
        """Create a new login response packet."""
        self.token = encrypted_token_bytes
        self.packet: bytes

    def to_bytes(self) -> bytes:
        """Encode a login response packet into a byte array."""
        logging.info("Creating login response")

        self.packet = super().to_bytes()

        self.packet += struct.pack(
            self.struct_format,
            len(self.token),
        )

        self.packet += self.token

        return self.packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[bytes]:
        """Decode a message response packet into its individual components.

        :param packet: The packet to be decoded.
        :raises ValueError: If the packet is invalid.
        :return: A tuple containing an encrypted session token.
        """
        _, payload = cls.split_packet(packet)

        return (payload,)
