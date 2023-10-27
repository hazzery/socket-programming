"""
Message type enum class test suite.
"""

import unittest

from src.message_type import MessageType


class TestMessageType(unittest.TestCase):
    """
    Test suite for MessageType enum class.
    """

    def test_read_lowercase(self) -> None:
        """Test that read is parsed correctly."""
        self.assertEqual(MessageType.READ, MessageType.from_str("read"))

    def test_read_uppercase(self) -> None:
        """Test that READ is parsed correctly."""
        self.assertEqual(MessageType.READ, MessageType.from_str("READ"))

    def test_create_lowercase(self) -> None:
        """Test that create is parsed correctly."""
        self.assertEqual(MessageType.CREATE, MessageType.from_str("create"))

    def test_create_uppercase(self) -> None:
        """Test that CREATE is parsed correctly."""
        self.assertEqual(MessageType.CREATE, MessageType.from_str("CREATE"))

    def test_response_lowercase(self) -> None:
        """Test that response is parsed correctly."""
        self.assertEqual(MessageType.RESPONSE, MessageType.from_str("response"))

    def test_response_uppercase(self) -> None:
        """Test that RESPONSE is parsed correctly."""
        self.assertEqual(MessageType.RESPONSE, MessageType.from_str("RESPONSE"))

    def test_invalid(self) -> None:
        """Test that invalid input raises a ValueError."""
        self.assertRaises(ValueError, MessageType.from_str, "invalid")
