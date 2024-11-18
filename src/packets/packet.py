"""Home to the ``Packet`` abstract class."""

import abc
import re
import struct
from typing import Any


class Packet(metaclass=abc.ABCMeta):
    """Abstract class for all packets.

    All classes inheriting ``Packet`` must specify  ``struct_format`` in
    their class attributes. The format of ``struct_format`` is as described in
    https://docs.python.org/3/library/struct.html.

    Example::

        class MyPacket(Packet, struct_format="!HBBH"):
            pass
    """

    STRUCT_FORMAT_REGEX = re.compile("^[@=<>!]?[xcbB?hHiIlLqQnNefdspP]+$")

    struct_format: str

    @abc.abstractmethod
    def __init__(self, *args: tuple[Any, ...]) -> None:
        """Initialise the packet.

        :param args: All arguments needed to initialise the packet.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def to_bytes(self) -> bytes:
        """Convert the packet into a ``bytes`` object.

        :return: A ``bytes`` object encoding the packet's message type.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def decode_packet(cls, packet: bytes) -> tuple[Any, ...]:
        """Decode the packet into its individual fields.

        :param packet: The packet to decode.
        :return: A tuple of the decoded message type and the payload.
        """
        raise NotImplementedError

    @classmethod
    def split_packet(cls, packet: bytes) -> tuple[tuple[Any, ...], bytes]:
        """Split the packet into its header and payload.

        :param packet: The packet to split up.
        :return: A tuple containing:
            a tuple of the individual header fields,
            and the packet's payload.
        """
        header_size = struct.calcsize(cls.struct_format)
        header, payload = packet[:header_size], packet[header_size:]

        header_fields = struct.unpack(cls.struct_format, header)

        return header_fields, payload

    @classmethod
    def __init_subclass__(cls, *, struct_format: str) -> None:
        """Ensure ``struct_format`` attribute is present.

        All subclasses of ``Packet`` must specify a ``struct_format``
        in their class attributes. This is used for packing and
        unpacking the data into a minimal package.

        :param message_type: The type of message the packet will encode.
        :param struct_format: The format of the packet data for the ``struct`` module.

        :raises ValueError: if the provided struct format is invalid.
        """
        if not re.match(Packet.STRUCT_FORMAT_REGEX, struct_format):
            raise ValueError("Invalid struct format")

        super().__init_subclass__()
        cls.struct_format = struct_format
