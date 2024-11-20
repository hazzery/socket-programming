"""``ReadRequest`` class test suite."""

import unittest

from src.packets.read_request import ReadRequest


class TestReadRequestEncoding(unittest.TestCase):
    """Test suite for encoding ReadRequest packets."""

    def test_encode_zero_bytes(self) -> None:
        """Test that a read request encodes to an empty byte string."""
        packet = ReadRequest().to_bytes()
        self.assertEqual(b"", packet)
