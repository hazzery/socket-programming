import abc


class Record(metaclass=abc.ABCMeta):
    """
    Abstract class for all records
    """

    MAGIC_NUMBER = 0xAE73

    @abc.abstractmethod
    def __init__(self, *args):
        raise NotImplementedError

    @abc.abstractmethod
    def to_bytes(self) -> bytes:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_bytes(cls, record: bytes) -> "Record":
        raise NotImplementedError

    @abc.abstractmethod
    def decode(self) -> tuple:
        raise NotImplementedError
