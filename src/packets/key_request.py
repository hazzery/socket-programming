"""Public key request module.

Defines the KeyRequest class which is used to encode and decode
public key request packets.
"""

import struct

from src.packets.packet import Packet


class KeyRequest(Packet, struct_format="!H"):
    """Encode and decode public key request packets."""

    def __init__(self, user_name: str) -> None:
        """Create a key request packet."""
        self.user_name = user_name

    def to_bytes(self) -> bytes:
        """Encode the key request packet into a byte array."""
        packet = struct.pack(
            self.struct_format,
            len(self.user_name.encode()),
        )

        packet += self.user_name.encode()

        return packet

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
