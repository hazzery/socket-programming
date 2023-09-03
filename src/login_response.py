"""
Login response module
Defines class for encoding and decoding login response packets.
"""
from .message_type import MessageType
from .record import Record


class LoginResponse(Record):
    """
    The LoginResponse class is used to encode and decode login response packets.
    """
    def __init__(self, is_registered: bool):
        """
        Create a new login response packet.
        """
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
        # self.record.extend(self.encryption_key.product.to_bytes(4, "big"))
        # self.record.extend(self.encryption_key.exponent.to_bytes(4, "big"))

        return bytes(self.record)

    @classmethod
    def from_record(cls, record: bytes) -> "LoginResponse":
        pass

    def decode(self) -> tuple:
        pass
