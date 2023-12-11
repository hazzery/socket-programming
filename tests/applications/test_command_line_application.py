"""
Packet class test suite
"""
import unittest
from typing import Any

from src.packets.packet import Packet


class TestClientParseArguments(unittest.TestCase):
    """
    Test suite for Client class
    """

    def test_fail_subclass(self) -> None:
        """
        Test that we cannot subclass from CommandLineApplication without struct format
        """
        try:

            class NoStructFormat(Packet):
                """
                This class will not be created
                """

                def __init__(self, *args: tuple[Any, ...]):
                    pass

                def to_bytes(self) -> bytes:
                    return bytes()

                @classmethod
                def decode_packet(cls, packet: bytes) -> tuple[Any, ...]:
                    return ()

            NoStructFormat()

        except ValueError:
            pass
        else:
            self.fail("Did not raise, was able to subclass from CommandLineApplication")
