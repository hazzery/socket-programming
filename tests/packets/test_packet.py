"""Packet class test suite."""

from typing import Any

import pytest

from src.packets.packet import Packet


def test_fail_subclass() -> None:
    """Test Packet __init_subclass__ function.

    Ensure that we cannot subclass from Packet without specifying a struct format.
    """
    with pytest.raises(ValueError, match="Invalid struct format"):

        class NoStructFormat(
            Packet,
            struct_format="invalid format",
        ):
            """Invalid ``struct_format`` passed, so class will not be created."""

            def __init__(self, *args: tuple[Any, ...]) -> None:
                pass

            def to_bytes(self) -> bytes:
                return b""

            # ruff: noqa: ARG003
            @classmethod
            def decode_packet(cls, packet: bytes) -> tuple[Any, ...]:
                return ()
