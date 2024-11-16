"""Server class test suite."""

import unittest

from server import Server
from src.message_type import MessageType
from src.packets.packet import Packet
from src.packets.read_request import ReadRequest
from src.packets.read_response import ReadResponse

DUMMY_SESSION_TOKEN = b"01234567890123456789012345678901"


class TestServer(unittest.TestCase):
    """Test suite for Server class."""

    port_number = 12000
    hostname = "localhost"

    def test_construction(self) -> None:
        """Tests that a Server object can be constructed given correct arguments."""
        Server([str(TestServer.port_number)])

    def test_construction_raise_error(self) -> None:
        """Tests that a Server object cannot be constructed given invalid arguments."""
        self.assertRaises(
            SystemExit,
            Server,
            [str(TestServer.port_number), "Extra argument"],
        )

    def test_process_read_request(self) -> None:
        """Tests that Server objects correctly responds to read requests."""
        server = Server([str(TestServer.port_number)])

        sender_name = "Alice"
        receiver_name = "John"
        message = b"Hello John"

        server.sessions = {DUMMY_SESSION_TOKEN: receiver_name}
        server.messages[receiver_name] = [(sender_name, message)]

        request = ReadRequest(DUMMY_SESSION_TOKEN, receiver_name).to_bytes()

        _, _, packet = Packet.decode_packet(request)

        response = server.process_read_request(receiver_name, packet)
        message_type, session_token, payload = Packet.decode_packet(response)

        messages, more_messages = ReadResponse.decode_packet(payload)

        self.assertEqual(MessageType.READ_RESPONSE, message_type)
        self.assertEqual(None, session_token)
        self.assertEqual([(sender_name, message.decode())], messages)
        self.assertEqual(False, more_messages)
