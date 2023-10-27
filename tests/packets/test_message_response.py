"""
MessageResponse class test suite
"""
import unittest

from src.packets.packet import Packet
from src.message_type import MessageType
from src.packets.message_response import MessageResponse


class TestMessageResponse(unittest.TestCase):
    """
    Test suite for MessageResponse packets
    """

    def test_magic_number_encoding(self) -> None:
        """Tests that the magic number is encoded correctly"""
        messages: list[tuple[str, bytes]] = []
        packet = MessageResponse(messages).to_bytes()

        expected = Packet.MAGIC_NUMBER
        actual = (packet[0] << 8) | (packet[1] & 0xFF)
        self.assertEqual(expected, actual)

    def test_message_type_encoding(self) -> None:
        """Tests that the message type is encoded correctly"""
        messages: list[tuple[str, bytes]] = []
        packet = MessageResponse(messages).to_bytes()

        expected = MessageType.RESPONSE.value
        actual = packet[2]
        self.assertEqual(expected, actual)

    def test_num_messages_encoding(self) -> None:
        """Tests that the number of messages is encoded correctly"""
        messages = [("Harry", "Hello John!".encode()), ("John", "Hello Harry!".encode())]
        packet = MessageResponse(messages).to_bytes()

        expected = len(messages)
        actual = packet[3]
        self.assertEqual(expected, actual)

    def test_more_messages_encoding(self) -> None:
        """Tests that the more messages flag is encoded correctly"""
        messages: list[tuple[str, bytes]] = []
        packet = MessageResponse(messages).to_bytes()

        expected = False
        actual = packet[4]
        self.assertEqual(expected, actual)
