import unittest

from src.message_type import MessageType


class TestMessageType(unittest.TestCase):

    def test_read_lowercase(self):
        self.assertEquals(MessageType.READ, MessageType.from_str("read"))

    def test_read_uppercase(self):
        self.assertEquals(MessageType.READ, MessageType.from_str("READ"))

    def test_create_lowercase(self):
        self.assertEquals(MessageType.CREATE, MessageType.from_str("create"))

    def test_create_uppercase(self):
        self.assertEquals(MessageType.CREATE, MessageType.from_str("CREATE"))

    def test_response_lowercase(self):
        self.assertEquals(MessageType.RESPONSE, MessageType.from_str("response"))

    def test_response_uppercase(self):
        self.assertEquals(MessageType.RESPONSE, MessageType.from_str("RESPONSE"))

    def test_invalid(self):
        self.assertRaises(ValueError, MessageType.from_str, "invalid")
