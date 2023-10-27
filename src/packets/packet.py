"""
This module contains the abstract class for all packets.
"""

from typing import Any
import struct
import abc


class Packet(metaclass=abc.ABCMeta):
    """
    Abstract class for all packets.
    """

    MAGIC_NUMBER = 0xAE73

    struct_format: str

    @abc.abstractmethod
    def __init__(self, *args: tuple[Any, ...]):
        """
        Initialises the packet.
        :param args: All arguments needed to initialise the packet
        """
        raise NotImplementedError

    @abc.abstractmethod
    def to_bytes(self) -> bytes:
        """
        Converts the packet into a `bytes` object.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def decode_packet(cls, packet: bytes) -> tuple[Any, ...]:
        """
        Decodes the packet into a tuple of values.
        """
        raise NotImplementedError

    @classmethod
    def __init_subclass__(cls, struct_format: str | None = None, **kwargs: tuple[Any, ...]) -> None:
        """
        Ensures that subclasses of ``Packet`` specify a ``struct_format`` in their class attributes.
        :param struct_format: The format of the packet data for the ``struct`` module.
        :param kwargs: No additional kwargs will be accepted.
        """
        if not struct_format:
            raise ValueError("Must specify struct format")

        super().__init_subclass__(**kwargs)
        cls.struct_format = struct_format
