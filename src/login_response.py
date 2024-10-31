"""Login response module.

Defines class for encoding and decoding login response packets.
"""

import logging
import struct

from message_cipher.rsa_encrypter import RsaEncrypter

from src.message_type import MessageType
from src.packets.packet import Packet


class LoginResponse(Packet, struct_format="!HB?QQ"):
    """The LoginResponse class is used to encode and decode login response packets."""

    def __init__(self, is_registered: bool, encryption_key: RsaEncrypter) -> None:
        """Create a new login response packet.

        :param is_registered: ``True`` if the requesting user was registered.
        :param encryption_key: An RSA public key for encrypting messages.
        """
        """Create a new login response packet."""
        self.encryption_key = encryption_key
        self.is_registered = is_registered
        self.packet = b""

    def to_bytes(self) -> bytes:
        """Encode a login response packet into a byte array."""
        logging.info("Creating login response")

        self.packet = struct.pack(
            self.struct_format,
            Packet.MAGIC_NUMBER,
            MessageType.LOGIN.value,
            self.is_registered,
            self.encryption_key.product,
            self.encryption_key.exponent,
        )

        return self.packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[bool, RsaEncrypter]:
        """Decode a message response packet into its individual components.

        :param packet: The packet to be decoded.
        :raises ValueError: If the packet is invalid.
        :return: A tuple containing a boolean indicating if the
        """
        header_fields, _ = cls.split_packet(packet)
        magic_number, message_type, is_registered, product, exponent = header_fields

        if magic_number != Packet.MAGIC_NUMBER:
            raise ValueError("Invalid magic number when decoding message response")

        try:
            message_type = MessageType(message_type)
        except ValueError as error:
            raise ValueError(
                "Invalid message type when decoding message response",
            ) from error
        if message_type != MessageType.LOGIN:
            message = (
                f"Message type {message_type} found when decoding message response, "
                "expected LOGIN"
            )
            raise ValueError(message)

        encryption_key = RsaEncrypter(product, exponent)

        return is_registered, encryption_key
