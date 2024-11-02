"""Packet class test suite."""

import unittest
from typing import Any

from src.packets.packet import Packet


class TestClientParseArguments(unittest.TestCase):
    """Test suite for Client class."""

    def test_fail_subclass(self) -> None:
        """Test Packet __init_subclass__ function.

        Ensure that we cannot subclass from CommandLineApplication
        without specifying a struct format.
        """
        with self.assertRaises(ValueError):

            class NoStructFormat(Packet):
                """No ``struct_formatt`` passed so class will not be created."""

                def __init__(self, *args: tuple[Any, ...]) -> None:
                    pass

                def to_bytes(self) -> bytes:
                    return b""

                # ruff: noqa: ARG003
                @classmethod
                def decode_packet(cls, packet: bytes) -> tuple[Any, ...]:
                    return ()

            NoStructFormat()
