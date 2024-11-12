"""Public key response module.

Defines the KeyResponse class which is used to encode and decode
public key response packets.
"""

import logging
import struct

from message_cipher.rsa_encrypter import RsaEncrypter

from src.message_type import MessageType
from src.packets.packet import Packet


class KeyResponse(
    Packet,
    struct_format="!HH",
    message_type=MessageType.KEY_RESPONSE,
):
    """Encode and decode public key response packets."""

    def __init__(self, public_key: RsaEncrypter) -> None:
        """Create a key response packet."""
        self.public_key = public_key
        self.packet: bytes

    def to_bytes(self) -> bytes:
        """Encode the key response packet into a byte array."""
        logging.info("Creating key response")

        product = self.public_key.product.to_bytes(
            (self.public_key.product.bit_length() + 7) // 8,
        )

        exponent = self.public_key.exponent.to_bytes(
            (self.public_key.exponent.bit_length() + 7) // 8,
        )

        self.packet = super().to_bytes()

        self.packet += struct.pack(
            self.struct_format,
            len(product),
            len(exponent),
        )

        self.packet += product
        self.packet += exponent

        return self.packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[RsaEncrypter]:
        """Decode the key response packet into its individual components.

        :param packet: The packet to be decoded.
        :return: A tuple containing the public key of the requested user.
        """
        header_fields, payload = cls.split_packet(packet)
        product_length, exponent_length = header_fields

        product = int.from_bytes(payload[:product_length])
        index = product_length

        exponent = int.from_bytes(payload[index : index + exponent_length])

        public_key = RsaEncrypter(product, exponent)

        return (public_key,)
