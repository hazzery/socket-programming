"""``CreateRequest`` class test suite."""

import unittest

from src.message_type import MessageType
from src.packets.create_request import CreateRequest
from src.packets.packet import Packet


class TestMessageRequestEncoding(unittest.TestCase):
    """Test suite for encoding MessageRequest packets."""

    def test_user_name_length_encoding(self) -> None:
        """Tests that the length of the user's name is encoded correctly."""
        user_name = "Johnny"
        receiver_name = "Jarod"
        message = "Hello, World!"
        packet = CreateRequest(
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        _, payload = Packet.decode_packet(packet)

        expected = len(user_name.encode())
        actual = payload[0]
        self.assertEqual(expected, actual)

    def test_receiver_name_length_encoding(self) -> None:
        """Tests that the length of the receiver's name is encoded correctly."""
        user_name = "Jackson"
        receiver_name = "Jake"
        message = "Hello, World!"
        packet = CreateRequest(
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        _, payload = Packet.decode_packet(packet)

        expected = len(receiver_name.encode())
        actual = payload[1]
        self.assertEqual(expected, actual)

    def test_message_length_encoding(self) -> None:
        """Tests that the length of the message is encoded correctly."""
        user_name = "Jason"
        receiver_name = "Jay"
        message = "Hello, World!"
        packet = CreateRequest(
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        _, payload = Packet.decode_packet(packet)

        expected = len(message.encode())
        actual = (payload[2] << 8) | (payload[3] & 0xFF)
        self.assertEqual(expected, actual)

    def test_user_name_encoding(self) -> None:
        """Tests that the user's name is encoded correctly."""
        user_name = "Jason"
        receiver_name = "Jay"
        message = "Hello, World!"
        packet = CreateRequest(
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        _, payload = Packet.decode_packet(packet)

        expected = user_name
        actual = payload[4 : 4 + len(user_name.encode())].decode()
        self.assertEqual(expected, actual)

    def test_receiver_name_encoding(self) -> None:
        """Tests that the receiver's name is encoded correctly."""
        user_name = "Jeff"
        receiver_name = "Jesse"
        message = "Hello, World!"
        packet = CreateRequest(
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        _, payload = Packet.decode_packet(packet)

        start_index = 4 + len(user_name.encode())

        expected = receiver_name
        actual = payload[
            start_index : start_index + len(receiver_name.encode())
        ].decode()
        self.assertEqual(expected, actual)

    def test_message_encoding(self) -> None:
        """Tests that the message is encoded correctly."""
        user_name = "Julian"
        receiver_name = "Jimmy"
        message = "Hello, World!"
        packet = CreateRequest(
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        _, payload = Packet.decode_packet(packet)

        start_index = 4 + len(user_name.encode()) + len(receiver_name.encode())

        expected = message
        actual = payload[start_index : start_index + len(message.encode())].decode()
        self.assertEqual(expected, actual)


class TestCreateRequestDecoding(unittest.TestCase):
    """Test suite for decoding ``CreateRequest`` packets."""

    def setUp(self) -> None:
        """Set up the testing environment."""
        self.message_type = MessageType.CREATE
        self.user_name = "Jamie"
        self.receiver_name = "Jonty"
        self.message = "Hello, World!"

        packet = CreateRequest(
            self.user_name,
            self.receiver_name,
            self.message,
        ).to_bytes()
        _, self.packet = Packet.decode_packet(packet)

    def test_user_name_decoding(self) -> None:
        """Tests that the user's name is decoded correctly."""
        decoded_packet = CreateRequest.decode_packet(self.packet)

        expected = self.user_name
        actual = decoded_packet[0]
        self.assertEqual(expected, actual)

    def test_receiver_name_decoding(self) -> None:
        """Tests that the receiver's name is decoded correctly."""
        decoded_packet = CreateRequest.decode_packet(self.packet)

        expected = self.receiver_name
        actual = decoded_packet[1]
        self.assertEqual(expected, actual)

    def test_message_decoding(self) -> None:
        """Tests that the message is decoded correctly."""
        decoded_packet = CreateRequest.decode_packet(self.packet)

        expected = self.message
        actual = decoded_packet[2].decode()
        self.assertEqual(expected, actual)

    def test_insufficient_user_name_length(self) -> None:
        """Tests that an exception is raised if the user's name has a length of zero."""
        packet = bytearray(self.packet)
        packet[3] = 0

        self.assertRaises(ValueError, CreateRequest.decode_packet, packet)

    def test_insufficient_receiver_name_length(self) -> None:
        """Tests that an exception is raised.

        If the length of the receiver's name is zero.
        """
        packet = bytearray(self.packet)
        packet[1] = 0

        self.assertRaises(ValueError, CreateRequest.decode_packet, packet)

    def test_insufficient_message_length(self) -> None:
        """Tests that an exception is raised.

        If the length of the message is zero.
        """
        packet = bytearray(self.packet)
        packet[2] = 0
        packet[3] = 0

        self.assertRaises(ValueError, CreateRequest.decode_packet, packet)
