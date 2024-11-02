"""``MessageRequest`` class test suite."""

import unittest

from src.message_type import MessageType
from src.packets.message_request import MessageRequest
from src.packets.packet import Packet


class TestMessageRequestEncoding(unittest.TestCase):
    """Test suite for encoding MessageRequest packets."""

    def test_magic_number_encoding(self) -> None:
        """Tests that the magic number is encoded correctly."""
        message_type = MessageType.READ
        user_name = "Jamie"
        receiver_name = "Jonty"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type,
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        expected = Packet.MAGIC_NUMBER
        actual = (packet[0] << 8) | (packet[1] & 0xFF)
        self.assertEqual(expected, actual)

    def test_message_type_encoding(self) -> None:
        """Tests that the message type is encoded correctly."""
        message_type = MessageType.CREATE
        user_name = "Jamie"
        receiver_name = "Jonty"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type,
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        expected = message_type.value
        actual = packet[2]
        self.assertEqual(expected, actual)

    def test_user_name_length_encoding(self) -> None:
        """Tests that the length of the user's name is encoded correctly."""
        message_type = MessageType.CREATE
        user_name = "Johnny"
        receiver_name = "Jarod"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type,
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        expected = len(user_name.encode())
        actual = packet[3]
        self.assertEqual(expected, actual)

    def test_receiver_name_length_encoding(self) -> None:
        """Tests that the length of the receiver's name is encoded correctly."""
        message_type = MessageType.CREATE
        user_name = "Jackson"
        receiver_name = "Jake"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type,
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        expected = len(receiver_name.encode())
        actual = packet[4]
        self.assertEqual(expected, actual)

    def test_message_length_encoding(self) -> None:
        """Tests that the length of the message is encoded correctly."""
        message_type = MessageType.CREATE
        user_name = "Jason"
        receiver_name = "Jay"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type,
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        expected = len(message.encode())
        actual = (packet[5] << 8) | (packet[6] & 0xFF)
        self.assertEqual(expected, actual)

    def test_user_name_encoding(self) -> None:
        """Tests that the user's name is encoded correctly."""
        message_type = MessageType.CREATE
        user_name = "Jason"
        receiver_name = "Jay"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type,
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        expected = user_name
        actual = packet[7 : 7 + len(user_name.encode())].decode()
        self.assertEqual(expected, actual)

    def test_receiver_name_encoding(self) -> None:
        """Tests that the receiver's name is encoded correctly."""
        message_type = MessageType.CREATE
        user_name = "Jeff"
        receiver_name = "Jesse"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type,
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        start_index = 7 + len(user_name.encode())

        expected = receiver_name
        actual = packet[
            start_index : start_index + len(receiver_name.encode())
        ].decode()
        self.assertEqual(expected, actual)

    def test_message_encoding(self) -> None:
        """Tests that the message is encoded correctly."""
        message_type = MessageType.CREATE
        user_name = "Julian"
        receiver_name = "Jimmy"
        message = "Hello, World!"
        packet = MessageRequest(
            message_type,
            user_name,
            receiver_name,
            message,
        ).to_bytes()

        start_index = 7 + len(user_name.encode()) + len(receiver_name.encode())

        expected = message
        actual = packet[start_index : start_index + len(message.encode())].decode()
        self.assertEqual(expected, actual)


class TestMessageRequestDecoding(unittest.TestCase):
    """Test suite for decoding ``MessageRequest`` packets."""

    def setUp(self) -> None:
        """Set up the testing environment."""
        self.message_type = MessageType.CREATE
        self.user_name = "Jamie"
        self.receiver_name = "Jonty"
        self.message = "Hello, World!"
        self.packet = MessageRequest(
            self.message_type,
            self.user_name,
            self.receiver_name,
            self.message,
        ).to_bytes()

    def test_message_type_decoding(self) -> None:
        """Tests that the message type is decoded correctly."""
        decoded_packet = MessageRequest.decode_packet(self.packet)
        expected = self.message_type
        actual = decoded_packet[0]
        self.assertEqual(expected, actual)

    def test_user_name_decoding(self) -> None:
        """Tests that the user's name is decoded correctly."""
        decoded_packet = MessageRequest.decode_packet(self.packet)
        expected = self.user_name
        actual = decoded_packet[1]
        self.assertEqual(expected, actual)

    def test_receiver_name_decoding(self) -> None:
        """Tests that the receiver's name is decoded correctly."""
        decoded_packet = MessageRequest.decode_packet(self.packet)
        expected = self.receiver_name
        actual = decoded_packet[2]
        self.assertEqual(expected, actual)

    def test_message_decoding(self) -> None:
        """Tests that the message is decoded correctly."""
        decoded_packet = MessageRequest.decode_packet(self.packet)
        expected = self.message
        actual = decoded_packet[3].decode()
        self.assertEqual(expected, actual)

    def test_incorrect_magic_number(self) -> None:
        """Tests that an exception is raised if the magic number is incorrect."""
        packet = bytearray(self.packet)
        packet[0] = 0
        self.packet = bytes(packet)

        self.assertRaises(ValueError, MessageRequest.decode_packet, self.packet)

    def test_invalid_message_type(self) -> None:
        """Tests that an exception is raised if the message type is invalid."""
        packet = bytearray(self.packet)
        packet[2] = 0
        self.packet = bytes(packet)

        self.assertRaises(ValueError, MessageRequest.decode_packet, self.packet)

    def test_response_message_type(self) -> None:
        """Tests that an exception is raised if the message type is RESPONSE."""
        packet = bytearray(self.packet)
        packet[2] = 3
        self.packet = bytes(packet)

        self.assertRaises(ValueError, MessageRequest.decode_packet, self.packet)

    def test_insufficient_user_name_length(self) -> None:
        """Tests that an exception is raised if the user's name has a length of zero."""
        packet = bytearray(self.packet)
        packet[3] = 0
        self.packet = bytes(packet)

        self.assertRaises(ValueError, MessageRequest.decode_packet, self.packet)

    def test_non_zero_receiver_name_length_for_read(self) -> None:
        """Tests that an exception is raised.

        If the length of the receiver's name is non-zero for a read request.
        """
        packet = bytearray(self.packet)
        packet[2] = MessageType.READ.value
        packet[4] = 1
        self.packet = bytes(packet)

        self.assertRaises(ValueError, MessageRequest.decode_packet, self.packet)

    def test_non_zero_message_length_for_read(self) -> None:
        """Tests that an exception is raised.

        If the length of the message is non-zero for a read request.
        """
        packet = bytearray(self.packet)
        packet[2] = MessageType.READ.value
        packet[4] = 0
        packet[6] = 1
        self.packet = bytes(packet)

        self.assertRaises(ValueError, MessageRequest.decode_packet, self.packet)

    def test_insufficient_receiver_name_length_for_create(self) -> None:
        """Tests that an exception is raised.

        If the length of the receiver's name is zero for a create request.
        """
        packet = bytearray(self.packet)
        packet[2] = MessageType.CREATE.value
        packet[4] = 0
        self.packet = bytes(packet)

        self.assertRaises(ValueError, MessageRequest.decode_packet, self.packet)

    def test_insufficient_message_length_for_create(self) -> None:
        """Tests that an exception is raised.

        If the length of the message is zero for a create request.
        """
        packet = bytearray(self.packet)
        packet[2] = MessageType.CREATE.value
        packet[5] = 0
        packet[6] = 0
        self.packet = bytes(packet)

        self.assertRaises(ValueError, MessageRequest.decode_packet, self.packet)
