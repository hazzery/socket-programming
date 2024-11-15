"""Home to the ``ReadReqeust`` class."""

import logging
import struct

from src.message_type import MessageType

from .packet import Packet

logger = logging.getLogger(__name__)


class ReadRequest(Packet, struct_format="!B", message_type=MessageType.READ):
    """Encoding and decoding of read request packets.

    Usage:
        read_request = ReadRequest("Recipient name")
        packet = read_request.to_bytes()

        read_request = ReadRequest.decode_packet(packet)
        (recipient_name,) = read_request.decode()
    """

    def __init__(
        self,
        session_token: bytes,
        user_name: str,
    ) -> None:
        """Encode a read request packet.

        :param user_name: The name of the user sending the read request.
        """
        super().__init__(session_token=session_token)
        self.user_name = user_name
        self.packet: bytes

    def to_bytes(self) -> bytes:
        """Return the read request packet.

        :return: An array of bytes holding the message request.
        """
        logger.debug("Creating READ request from %s", self.user_name)

        self.packet = super().to_bytes()

        self.packet += struct.pack(
            self.struct_format,
            len(self.user_name.encode()),
        )

        self.packet += self.user_name.encode()

        return self.packet

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[str]:
        """Decode a read request packet.

        :param packet: An array of bytes containing the read request.
        :return: A tuple containing the user requesting their messages.
        """
        header_fields, payload = cls.split_packet(packet)
        (user_name_size,) = header_fields

        if user_name_size < 1:
            raise ValueError(
                "Received message request with insufficient user name length",
            )

        user_name = payload.decode()

        return (user_name,)
