"""``ReadRequest`` class test suite."""

import unittest

from src.packets.packet import Packet
from src.packets.read_request import ReadRequest


class TestReadRequestEncoding(unittest.TestCase):
    """Test suite for encoding ReadRequest packets."""

    def test_user_name_length_encoding(self) -> None:
        """Tests that the length of the user's name is encoded correctly."""
        user_name = "Johnny"
        packet = ReadRequest(user_name).to_bytes()
        _, payload = Packet.decode_packet(packet)

        expected = len(user_name.encode())
        actual = payload[0]
        self.assertEqual(expected, actual)

    def test_user_name_encoding(self) -> None:
        """Tests that the user's name is placed correctly in the packet."""
        user_name = "Johnny"
        packet = ReadRequest(user_name).to_bytes()
        _, payload = Packet.decode_packet(packet)

        expected = user_name
        actual = payload[1:].decode()
        self.assertEqual(expected, actual)


class TestReadRequestDecoding(unittest.TestCase):
    """Test suite for decoding ``ReadRequest`` packets."""

    def setUp(self) -> None:
        """Set up the testing environment."""
        self.user_name = "Jamie"

        packet = ReadRequest(self.user_name).to_bytes()
        _, self.packet = Packet.decode_packet(packet)

    def test_user_name_decoding(self) -> None:
        """Tests that the user's name is decoded correctly."""
        decoded_packet = ReadRequest.decode_packet(self.packet)

        expected = self.user_name
        actual = decoded_packet[0]
        self.assertEqual(expected, actual)

    def test_insufficient_user_name_length(self) -> None:
        """Tests that an exception is raised if the user's name has a length of zero."""
        packet = bytearray(self.packet)
        packet[0] = 0
        self.packet = bytes(packet)

        self.assertRaises(ValueError, ReadRequest.decode_packet, self.packet)
