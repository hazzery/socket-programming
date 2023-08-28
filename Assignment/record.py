from pythonlangutil.overload import Overload, signature
import abc


class Record(metaclass=abc.ABCMeta):
    """
    Abstract class for all records
    """

    MAGIC_NUMBER = 0xAE73

    @Overload
    @signature("tuple")
    @abc.abstractmethod
    def __init__(self, *args):
        self.record: bytearray
        raise NotImplementedError

    @__init__.overload
    @signature("bytes")
    @abc.abstractmethod
    def __init__(self, record: bytes):
        raise NotImplementedError

