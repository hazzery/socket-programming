"""MessageResponse class test suite."""

import unittest

from src.packets.packet import Packet
from src.packets.read_response import ReadResponse


class TestMessageResponseEncoding(unittest.TestCase):
    """Test suite for encoding MessageResponse packets."""

    def test_num_messages_encoding(self) -> None:
        """Tests that the number of messages is encoded correctly."""
        messages = [
            ("Harry", b"Hello John!"),
            ("John", b"Hello Harry!"),
        ]
        packet = ReadResponse(messages).to_bytes()
        _, packet = Packet.decode_packet(packet)

        expected = len(messages)
        actual = packet[0]
        self.assertEqual(expected, actual)

    def test_more_messages_encoding(self) -> None:
        """Tests that the more messages flag is encoded correctly."""
        messages: list[tuple[str, bytes]] = []
        packet = ReadResponse(messages).to_bytes()
        _, packet = Packet.decode_packet(packet)

        expected = False
        actual = packet[1]
        self.assertEqual(expected, actual)


class TestMessageResponseDecoding(unittest.TestCase):
    """Test suite for decoding MessageResponse packets."""

    def test_messages_decoding(self) -> None:
        """Tests that the messages are decoded correctly."""
        messages = [
            ("Harry", b"Hello John!"),
            ("John", b"Hello Harry!"),
        ]
        packet = ReadResponse(messages).to_bytes()

        _, packet = Packet.decode_packet(packet)

        expected = [
            ("Harry", "Hello John!"),
            ("John", "Hello Harry!"),
        ]
        actual = ReadResponse.decode_packet(packet)[0]
        self.assertEqual(expected, actual)

    def test_more_messages_decoding_false(self) -> None:
        """Tests that the more messages flag is decoded correctly."""
        messages = [
            ("Harry", b"Hello John!"),
            ("John", b"Hello Harry!"),
        ]
        packet = ReadResponse(messages).to_bytes()
        _, packet = Packet.decode_packet(packet)

        expected = False
        actual = ReadResponse.decode_packet(packet)[1]
        self.assertEqual(expected, actual)

    def test_more_messages_decoding_true(self) -> None:
        """Tests that the more messages flag is decoded correctly."""
        messages = [("Harry", b"Hello John!")] * 256
        packet = ReadResponse(messages).to_bytes()

        _, packet = Packet.decode_packet(packet)

        expected = True
        actual = ReadResponse.decode_packet(packet)[1]
        self.assertEqual(expected, actual)
