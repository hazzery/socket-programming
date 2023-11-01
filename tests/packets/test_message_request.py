"""
MessageRequest class test suite
"""
import unittest

from src.packets.packet import Packet
from src.message_type import MessageType
from src.packets.message_request import MessageRequest


class TestMessageRequest(unittest.TestCase):
    """
    Test suite for MessageRequest packets
    """

    def test_magic_number_encoding(self) -> None:
        """Tests that the magic number is encoded correctly"""
        message_type = MessageType.CREATE
        user_name = "Jamie"
        receiver_name = "Jonty"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type, user_name, receiver_name, message
        ).to_bytes()

        expected = Packet.MAGIC_NUMBER
        actual = (packet[0] << 8) | (packet[1] & 0xFF)
        self.assertEqual(expected, actual)

    def test_message_type_encoding(self) -> None:
        """Tests that the message type is encoded correctly"""
        message_type = MessageType.CREATE
        user_name = "Jamie"
        receiver_name = "Jonty"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type, user_name, receiver_name, message
        ).to_bytes()

        expected = message_type.value
        actual = packet[2]
        self.assertEqual(expected, actual)

    def test_user_name_length_encoding(self) -> None:
        """Tests that the length of the user's name is encoded correctly"""
        message_type = MessageType.CREATE
        user_name = "Johnny"
        receiver_name = "Jarod"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type, user_name, receiver_name, message
        ).to_bytes()

        expected = len(user_name.encode())
        actual = packet[3]
        self.assertEqual(expected, actual)

    def test_receiver_name_length_encoding(self) -> None:
        """Tests that the length of the receiver's name is encoded correctly"""
        message_type = MessageType.CREATE
        user_name = "Jackson"
        receiver_name = "Jake"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type, user_name, receiver_name, message
        ).to_bytes()

        expected = len(receiver_name.encode())
        actual = packet[4]
        self.assertEqual(expected, actual)

    def test_message_length_encoding(self) -> None:
        """Tests that the length of the message is encoded correctly"""
        message_type = MessageType.CREATE
        user_name = "Jason"
        receiver_name = "Jay"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type, user_name, receiver_name, message
        ).to_bytes()

        expected = len(message.encode())
        actual = (packet[5] << 8) | (packet[6] & 0xFF)
        self.assertEqual(expected, actual)

    def test_user_name_encoding(self) -> None:
        """Tests that the user's name is encoded correctly"""
        message_type = MessageType.CREATE
        user_name = "Jason"
        receiver_name = "Jay"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type, user_name, receiver_name, message
        ).to_bytes()

        expected = user_name
        actual = packet[7 : 7 + len(user_name.encode())].decode()
        self.assertEqual(expected, actual)

    def test_receiver_name_encoding(self) -> None:
        """Tests that the receiver's name is encoded correctly"""
        message_type = MessageType.CREATE
        user_name = "Jeff"
        receiver_name = "Jesse"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type, user_name, receiver_name, message
        ).to_bytes()

        start_index = 7 + len(user_name.encode())

        expected = receiver_name
        actual = packet[
            start_index : start_index + len(receiver_name.encode())
        ].decode()
        self.assertEqual(expected, actual)

    def test_message_encoding(self) -> None:
        """Tests that the message is encoded correctly"""
        message_type = MessageType.CREATE
        user_name = "Julian"
        receiver_name = "Jimmy"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type, user_name, receiver_name, message
        ).to_bytes()

        start_index = 7 + len(user_name.encode()) + len(receiver_name.encode())

        expected = message
        actual = packet[start_index : start_index + len(message.encode())].decode()
        self.assertEqual(expected, actual)
