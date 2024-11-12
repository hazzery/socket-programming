"""Login request module.

Defines the LoginRequest class which is used to encode and decode login request packets.
"""

import logging
import struct
from typing import Any

from src.message_type import MessageType
from src.packets.packet import Packet


class LoginRequest(Packet, struct_format="!HBB", message_type=MessageType.LOGIN):
    """The LoginRequest class is used to encode and decode login request packets."""

    def __init__(self, user_name: str) -> None:
        """Create a login request packet."""
        self.user_name = user_name
        self.packet = b""

    def to_bytes(self) -> bytes:
        """Encode the login request packet into a byte array."""
        logging.info("Creating log-in request as %s", self.user_name)

        self.packet = struct.pack(
            self.struct_format,
            len(self.user_name.encode()),
        )

        self.packet += self.user_name.encode()

        return self.packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[Any, ...]:
        """Decode the login request packet into its individual components.

        :param packet: The packet to be decoded.
        :return: A tuple containing the username.
        """
        _, payload = cls.split_packet(packet)

        user_name = payload.decode()

        return (user_name,)
