"""
This module contains the abstract class for all records
"""

import abc


class Record(metaclass=abc.ABCMeta):
    """
    Abstract class for all records
    """

    MAGIC_NUMBER = 0xAE73

    @abc.abstractmethod
    def __init__(self, *args):
        """
        Initialises the record
        """
        raise NotImplementedError

    @abc.abstractmethod
    def to_bytes(self) -> bytes:
        """
        Converts the record into a bytes object
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_record(cls, record: bytes) -> "Record":
        """
        Creates a record from a bytes object
        """
        raise NotImplementedError

    @abc.abstractmethod
    def decode(self) -> tuple:
        """
        Decodes the record into a tuple of values
        """
        raise NotImplementedError
