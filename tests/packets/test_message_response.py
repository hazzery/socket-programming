"""MessageResponse class test suite."""

import unittest

from src.message_type import MessageType
from src.packets.message_response import MessageResponse
from src.packets.packet import Packet


class TestMessageResponseEncoding(unittest.TestCase):
    """Test suite for encoding MessageResponse packets."""

    def test_magic_number_encoding(self) -> None:
        """Tests that the magic number is encoded correctly."""
        messages: list[tuple[str, bytes]] = []
        packet = MessageResponse(messages).to_bytes()

        expected = Packet.MAGIC_NUMBER
        actual = (packet[0] << 8) | (packet[1] & 0xFF)
        self.assertEqual(expected, actual)

    def test_message_type_encoding(self) -> None:
        """Tests that the message type is encoded correctly."""
        messages: list[tuple[str, bytes]] = []
        packet = MessageResponse(messages).to_bytes()

        expected = MessageType.RESPONSE.value
        actual = packet[2]
        self.assertEqual(expected, actual)

    def test_num_messages_encoding(self) -> None:
        """Tests that the number of messages is encoded correctly."""
        messages = [
            ("Harry", b"Hello John!"),
            ("John", b"Hello Harry!"),
        ]
        packet = MessageResponse(messages).to_bytes()

        expected = len(messages)
        actual = packet[3]
        self.assertEqual(expected, actual)

    def test_more_messages_encoding(self) -> None:
        """Tests that the more messages flag is encoded correctly."""
        messages: list[tuple[str, bytes]] = []
        packet = MessageResponse(messages).to_bytes()

        expected = False
        actual = packet[4]
        self.assertEqual(expected, actual)


class TestMessageResponseDecoding(unittest.TestCase):
    """Test suite for decoding MessageResponse packets."""

    def test_messages_decoding(self) -> None:
        """Tests that the messages are decoded correctly."""
        messages = [
            ("Harry", b"Hello John!"),
            ("John", b"Hello Harry!"),
        ]
        packet = MessageResponse(messages).to_bytes()

        expected = [
            ("Harry", "Hello John!"),
            ("John", "Hello Harry!"),
        ]
        actual = MessageResponse.decode_packet(packet)[0]
        self.assertEqual(expected, actual)

    def test_more_messages_decoding_false(self) -> None:
        """Tests that the more messages flag is decoded correctly."""
        messages = [
            ("Harry", b"Hello John!"),
            ("John", b"Hello Harry!"),
        ]
        packet = MessageResponse(messages).to_bytes()

        expected = False
        actual = MessageResponse.decode_packet(packet)[1]
        self.assertEqual(expected, actual)

    def test_more_messages_decoding_true(self) -> None:
        """Tests that the more messages flag is decoded correctly."""
        messages = [("Harry", b"Hello John!")] * 256
        packet = MessageResponse(messages).to_bytes()

        expected = True
        actual = MessageResponse.decode_packet(packet)[1]
        self.assertEqual(expected, actual)

    def test_incorrect_magic_number(self) -> None:
        """Tests that a ``ValueError`` is raised when the magic number is incorrect."""
        messages: list[tuple[str, bytes]] = []
        packet = MessageResponse(messages).to_bytes()

        packet = bytearray(packet)
        packet[0] = 0x00

        self.assertRaises(ValueError, MessageResponse.decode_packet, bytes(packet))

    def test_invalid_message_type(self) -> None:
        """Tests that a ``ValueError`` is raised when the message type is invalid."""
        messages: list[tuple[str, bytes]] = []
        packet = MessageResponse(messages).to_bytes()

        packet = bytearray(packet)
        packet[2] = 4

        self.assertRaises(ValueError, MessageResponse.decode_packet, bytes(packet))

    def test_incorrect_message_type(self) -> None:
        """Tests that a ``ValueError`` is raised when the message type is incorrect."""
        messages: list[tuple[str, bytes]] = []
        packet = MessageResponse(messages).to_bytes()

        packet = bytearray(packet)
        packet[2] = MessageType.CREATE.value

        self.assertRaises(ValueError, MessageResponse.decode_packet, bytes(packet))
