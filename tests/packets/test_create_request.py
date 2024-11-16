"""``CreateRequest`` class test suite."""

import struct
import unittest

from src.message_type import MessageType
from src.packets.create_request import CreateRequest
from src.packets.packet import Packet

DUMMY_SESSION_TOKEN = b"01234567890123456789012345678901"
CREATE_PACKET_HEADER_SIZE = struct.calcsize(CreateRequest.struct_format)


class TestCreateRequestEncoding(unittest.TestCase):
    """Test suite for encoding MessageRequest packets."""

    def test_receiver_name_length_encoding(self) -> None:
        """Tests that the length of the receiver's name is encoded correctly."""
        receiver_name = "Jake"
        message = "Hello, World!"
        packet = CreateRequest(
            DUMMY_SESSION_TOKEN,
            receiver_name,
            message,
        ).to_bytes()

        _, _, payload = Packet.decode_packet(packet)

        expected = len(receiver_name.encode())
        actual = payload[0]
        self.assertEqual(expected, actual)

    def test_message_length_encoding(self) -> None:
        """Tests that the length of the message is encoded correctly."""
        receiver_name = "Jay"
        message = "Hello, World!"
        packet = CreateRequest(
            DUMMY_SESSION_TOKEN,
            receiver_name,
            message,
        ).to_bytes()

        _, _, payload = Packet.decode_packet(packet)

        expected = len(message.encode())
        actual = (payload[1] << 8) | (payload[2] & 0xFF)
        self.assertEqual(expected, actual)

    def test_receiver_name_encoding(self) -> None:
        """Tests that the receiver's name is encoded correctly."""
        receiver_name = "Jesse"
        message = "Hello, World!"
        packet = CreateRequest(
            DUMMY_SESSION_TOKEN,
            receiver_name,
            message,
        ).to_bytes()

        _, _, payload = Packet.decode_packet(packet)

        expected = receiver_name
        actual = payload[
            CREATE_PACKET_HEADER_SIZE : CREATE_PACKET_HEADER_SIZE
            + len(receiver_name.encode())
        ].decode()
        self.assertEqual(expected, actual)

    def test_message_encoding(self) -> None:
        """Tests that the message is encoded correctly."""
        receiver_name = "Jimmy"
        message = "Hello, World!"
        packet = CreateRequest(
            DUMMY_SESSION_TOKEN,
            receiver_name,
            message,
        ).to_bytes()

        _, _, payload = Packet.decode_packet(packet)

        start_index = CREATE_PACKET_HEADER_SIZE + len(receiver_name.encode())

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
            DUMMY_SESSION_TOKEN,
            self.receiver_name,
            self.message,
        ).to_bytes()
        _, _, self.packet = Packet.decode_packet(packet)

    def test_receiver_name_decoding(self) -> None:
        """Tests that the receiver's name is decoded correctly."""
        decoded_packet = CreateRequest.decode_packet(self.packet)

        expected = self.receiver_name
        actual = decoded_packet[0]
        self.assertEqual(expected, actual)

    def test_message_decoding(self) -> None:
        """Tests that the message is decoded correctly."""
        decoded_packet = CreateRequest.decode_packet(self.packet)

        expected = self.message
        actual = decoded_packet[1].decode()
        self.assertEqual(expected, actual)

    def test_insufficient_receiver_name_length(self) -> None:
        """Tests that an exception is raised.

        If the length of the receiver's name is zero.
        """
        packet = bytearray(self.packet)
        packet[0] = 0

        self.assertRaises(ValueError, CreateRequest.decode_packet, packet)

    def test_insufficient_message_length(self) -> None:
        """Tests that an exception is raised.

        If the length of the message is zero.
        """
        packet = bytearray(self.packet)
        packet[1] = 0
        packet[2] = 0

        self.assertRaises(ValueError, CreateRequest.decode_packet, packet)
