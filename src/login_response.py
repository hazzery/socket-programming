"""
Login response module
Defines class for encoding and decoding login response packets.
"""
from message_cipher.rsa_encrypter import RsaEncrypter

from .message_type import MessageType
from .record import Record


class LoginResponse(Record):
    """
    The LoginResponse class is used to encode and decode login response packets.
    """
    def __init__(self, is_registered: bool, encryption_key: RsaEncrypter):
        """
        Create a new login response packet.
        """
        self.encryption_key = encryption_key
        self.is_registered = is_registered
        self.record = bytearray(3)

    def to_bytes(self) -> bytes:
        """
        Encode a login response packet into a byte array.
        """
        self.record[0] = Record.MAGIC_NUMBER >> 8
        self.record[1] = Record.MAGIC_NUMBER & 0xFF
        self.record[2] = MessageType.LOGIN.value
        self.record[3] = self.is_registered
        self.record.extend(self.encryption_key.product.to_bytes(4, "big"))
        self.record.extend(self.encryption_key.exponent.to_bytes(4, "big"))

        return bytes(self.record)

    @classmethod
    def from_record(cls, record: bytes) -> "LoginResponse":
        """
        Decode a login response packet from a byte array.
        """
        message_type = Record.validate_record(record)
        if message_type != MessageType.LOGIN:
            raise ValueError(f"Message type {message_type} found when decoding login response, "
                             f"expected LOGIN")

        is_registered = bool(record[3])
        product = int.from_bytes(record[4:8], "big")
        exponent = int.from_bytes(record[8:12], "big")

        encryption_key = RsaEncrypter(product, exponent)
        return cls(is_registered, encryption_key)

    def decode(self) -> tuple[bool, RsaEncrypter]:
        """
        Decodes the login response packet
        :return: A tuple containing the boolean value of is_registered and the encryption key
        """
        return self.is_registered, self.encryption_key
