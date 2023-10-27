"""
This module contains the abstract class for all packets.
"""

from typing import Any
import abc


class Packet(metaclass=abc.ABCMeta):
    """
    Abstract class for all packets.
    """

    MAGIC_NUMBER = 0xAE73

    @property
    @abc.abstractmethod
    def structure_format(self) -> str:
        """
        Gets the format of the packet for the struct module
        """
        raise NotImplementedError

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
