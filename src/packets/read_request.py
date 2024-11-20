"""Home to the ``ReadReqeust`` class."""

import logging

from src.packets.packet import Packet

logger = logging.getLogger(__name__)


class ReadRequest(Packet, struct_format="!x"):
    """Encoding and decoding of read request packets.

    Usage:
        read_request = ReadRequest("Recipient name")
        packet = read_request.to_bytes()

        read_request = ReadRequest.decode_packet(packet)
        (recipient_name,) = read_request.decode()
    """

    def __init__(self) -> None:
        """Encode a read request packet.

        :param user_name: The name of the user sending the read request.
        """

    def to_bytes(self) -> bytes:
        """Return the read request packet.

        :return: An empty string of bytes.
        """
        return b""

    @classmethod
    def decode_packet(cls, packet: bytes) -> tuple[()]:  # noqa: ARG003
        """Decode a read request packet.

        :param packet: An array of bytes containing the read request.
        :return: An empty tuple
        """
        return ()
