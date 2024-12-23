"""``ReadRequest`` class test suite."""

from src.packets.read_request import ReadRequest


def test_encode_zero_bytes() -> None:
    """Test that a read request encodes to an empty byte string."""
    packet = ReadRequest().to_bytes()
    assert packet == b""
