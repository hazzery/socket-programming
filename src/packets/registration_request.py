"""Registration request module.

Defines the RegistrationRequest class which is used to encode and decode
registration request packets.
"""

import struct

import rsa

from src.packets.packet import Packet


class RegistrationRequest(Packet, struct_format="!BHH"):
    """Encode and decode registration request packets."""

    def __init__(self, user_name: str, public_key: rsa.PublicKey) -> None:
        """Create a login request packet."""
        self.user_name = user_name
        self.public_key = public_key

    def to_bytes(self) -> bytes:
        """Encode the registration request packet into a byte array."""
        user_name = self.user_name.encode()

        product = self.public_key.n.to_bytes(
            (self.public_key.n.bit_length() + 7) // 8,
        )

        exponent = self.public_key.e.to_bytes(
            (self.public_key.e.bit_length() + 7) // 8,
        )

        packet = struct.pack(
            self.struct_format,
            len(user_name),
            len(product),
            len(exponent),
        )

        packet += user_name
        packet += product
        packet += exponent

        return packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[str, rsa.PublicKey]:
        """Decode the registration request packet into its individual components.

        :param packet: The packet to be decoded
        :return: A tuple containing the username and public key
        """
        header_fields, payload = cls.split_packet(packet)
        user_name_length, product_length, exponent_length = header_fields

        user_name = payload[:user_name_length].decode()
        index = user_name_length

        product = int.from_bytes(payload[index : index + product_length])
        index += product_length

        exponent = int.from_bytes(payload[index : index + exponent_length])

        return user_name, rsa.PublicKey(product, exponent)
