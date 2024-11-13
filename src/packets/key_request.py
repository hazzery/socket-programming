"""Public key request module.

Defines the KeyRequest class which is used to encode and decode
public key request packets.
"""

import logging
import struct

from src.message_type import MessageType
from src.packets.packet import Packet


class KeyRequest(
    Packet,
    struct_format="!H",
    message_type=MessageType.KEY_REQUEST,
):
    """Encode and decode public key request packets."""

    def __init__(self, user_name: str) -> None:
        """Create a key request packet."""
        self.user_name = user_name
        self.packet: bytes

    def to_bytes(self) -> bytes:
        """Encode the key request packet into a byte array."""
        logging.debug("Creating key request for %s", self.user_name)

        self.packet = super().to_bytes()

        self.packet += struct.pack(
            self.struct_format,
            len(self.user_name.encode()),
        )

        self.packet += self.user_name.encode()

        return self.packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[str]:
        """Decode the key request packet into its individual components.

        :param packet: The packet to be decoded.
        :return: A tuple containing the username of the user who's key
        is being requested.
        """
        _, payload = cls.split_packet(packet)

        user_name = payload.decode()

        return (user_name,)
