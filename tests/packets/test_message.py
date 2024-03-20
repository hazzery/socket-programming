"""
Message class test suite
"""

import unittest

from src.packets.message import Message


class TestMessage(unittest.TestCase):
    """
    Test suite for Message packets
    """

    def test_sender_length_encoding(self) -> None:
        """Tests that the length of the sender's name is encoded correctly"""
        sender_name = "John"
        message_bytes = "Hello, World!".encode()
        packet = Message(sender_name, message_bytes).to_bytes()

        expected = len(sender_name.encode())
        actual = packet[0]
        self.assertEqual(expected, actual)

    def test_message_length_encoding(self) -> None:
        """Tests that the length of the message is encoded correctly"""
        sender_name = "Jack"
        message_bytes = "Hello, World!".encode()
        packet = Message(sender_name, message_bytes).to_bytes()

        expected = len(message_bytes)
        actual = (packet[1] << 8) | (packet[2] & 0xFF)
        self.assertEqual(expected, actual)

    def test_sender_name_encoding(self) -> None:
        """Tests that the sender's name is encoded correctly"""
        sender_name = "Jacob"
        message_bytes = "Hello, World!".encode()
        packet = Message(sender_name, message_bytes).to_bytes()

        expected = sender_name
        actual = packet[3 : 3 + len(sender_name.encode())].decode()
        self.assertEqual(expected, actual)

    def test_message_encoding(self) -> None:
        """Tests that the message is encoded correctly"""
        sender_name = "James"
        message_bytes = "Hello, World!".encode()
        packet = Message(sender_name, message_bytes).to_bytes()

        starting_index = 3 + len(sender_name.encode())
        expected = message_bytes.decode()
        actual = packet[starting_index : starting_index + len(message_bytes)].decode()
        self.assertEqual(expected, actual)
