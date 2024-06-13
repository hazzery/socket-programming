"""Home to the ``Packet`` abstract class."""

from typing import Any
import struct
import abc


class Packet(metaclass=abc.ABCMeta):
    """Abstract class for all packets.

    All classes inheriting ``Packet`` must specify ``struct_format``
    in their class attributes. The format of ``struct_format`` is as
    described in https://docs.python.org/3/library/struct.html

    Example::

        class MyPacket(Packet, struct_format="!HBBH"):
            pass
    """

    MAGIC_NUMBER = 0xAE73

    struct_format: str

    @abc.abstractmethod
    def __init__(self, *args: tuple[Any, ...]):
        """Initialise the packet.

        :param args: All arguments needed to initialise the packet.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def to_bytes(self) -> bytes:
        """Convert the packet into a ``bytes`` object.

        :return: A ``bytes`` object encoding individual fields of the packet.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def decode_packet(cls, packet: bytes) -> tuple[Any, ...]:
        """Decode the packet into a tuple of values.

        :param packet: The packet to decode.
        :return: A tuple of the decoded values extracted from the packet.
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
    def __init_subclass__(
        cls, struct_format: str | None = None, **kwargs: tuple[Any, ...]
    ) -> None:
        """Ensure that subclasses of ``Packet`` specify a ``struct_format`` in their class attributes.

        :param struct_format: The format of the packet data for the ``struct`` module.
        :param kwargs: No additional kwargs will be accepted.
        """
        if not struct_format:
            raise ValueError("Must specify struct format")

        super().__init_subclass__(**kwargs)
        cls.struct_format = struct_format
