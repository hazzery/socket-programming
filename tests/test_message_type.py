"""
Message type enum class test suite.
"""

import unittest

from src.message_type import MessageType


class TestMessageType(unittest.TestCase):
    """
    Test suite for MessageType enum class.
    """

    def test_read_lowercase(self):
        self.assertEquals(MessageType.READ, MessageType.from_str("read"))
        """Test that read is parsed correctly."""

    def test_read_uppercase(self):
        self.assertEquals(MessageType.READ, MessageType.from_str("READ"))
        """Test that READ is parsed correctly."""

    def test_create_lowercase(self):
        self.assertEquals(MessageType.CREATE, MessageType.from_str("create"))
        """Test that create is parsed correctly."""

    def test_create_uppercase(self):
        self.assertEquals(MessageType.CREATE, MessageType.from_str("CREATE"))
        """Test that CREATE is parsed correctly."""

    def test_response_lowercase(self):
        self.assertEquals(MessageType.RESPONSE, MessageType.from_str("response"))
        """Test that response is parsed correctly."""

    def test_response_uppercase(self):
        self.assertEquals(MessageType.RESPONSE, MessageType.from_str("RESPONSE"))
        """Test that RESPONSE is parsed correctly."""

    def test_invalid(self):
        """Test that invalid input raises a ValueError."""
        self.assertRaises(ValueError, MessageType.from_str, "invalid")
