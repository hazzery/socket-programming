"""Public key response module.

Defines the KeyResponse class which is used to encode and decode
public key response packets.
"""

import logging
import struct

import rsa

from src.message_type import MessageType
from src.packets.packet import Packet


class KeyResponse(
    Packet,
    struct_format="!HH",
    message_type=MessageType.KEY_RESPONSE,
):
    """Encode and decode public key response packets."""

    def __init__(self, public_key: rsa.PublicKey | None) -> None:
        """Create a key response packet."""
        super().__init__()
        self.public_key = public_key

    def to_bytes(self) -> bytes:
        """Encode the key response packet into a byte array."""
        logging.info("Creating key response")

        packet = super().to_bytes()

        if self.public_key is None:
            packet += struct.pack(self.struct_format, 0, 0)
            return packet

        product = self.public_key.n.to_bytes(
            (self.public_key.n.bit_length() + 7) // 8,
        )

        exponent = self.public_key.e.to_bytes(
            (self.public_key.e.bit_length() + 7) // 8,
        )

        packet += struct.pack(
            self.struct_format,
            len(product),
            len(exponent),
        )

        packet += product
        packet += exponent

        return packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[rsa.PublicKey | None]:
        """Decode the key response packet into its individual components.

        :param packet: The packet to be decoded.
        :return: A tuple containing the public key of the requested user.
        """
        header_fields, payload = cls.split_packet(packet)
        product_length, exponent_length = header_fields

        if product_length == 0 or exponent_length == 0:
            return (None,)

        product = int.from_bytes(payload[:product_length])
        index = product_length

        exponent = int.from_bytes(payload[index : index + exponent_length])

        public_key = rsa.PublicKey(product, exponent)

        return (public_key,)
