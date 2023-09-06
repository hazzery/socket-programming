"""
This module contains the abstract class for all records
"""

import abc

from message_type import MessageType


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

    @staticmethod
    def validate_record(record) -> MessageType:
        """
        Checks the magic number is correct
        """
        magic_number = record[0] << 8 | record[1]
        if magic_number != Record.MAGIC_NUMBER:
            raise ValueError("Invalid magic number when decoding message response")

        try:
            return MessageType(record[2])
        except ValueError as error:
            raise ValueError("Invalid message type when decoding message response") from error

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
