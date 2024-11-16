"""Client class test suite."""

import socket
import unittest

from client import Client
from src.message_type import MessageType
from src.packets.create_request import CreateRequest
from src.packets.packet import Packet

DUMMY_SESSION_TOKEN = b"01234567890123456789012345678901"


class TestClient(unittest.TestCase):
    """Test suite for Client class."""

    hostname = "localhost"
    port_number = 12000

    def test_construction(self) -> None:
        """Tests that a Client object can be constructed given correct arguments."""
        Client([TestClient.hostname, str(TestClient.port_number), "Alice", "create"])

    def test_construction_raise_error(self) -> None:
        """Tests that a Client object cannot be constructed given invalid arguments."""
        self.assertRaises(
            SystemExit,
            Client,
            ["invalid", str(TestClient.port_number), "Alice", "create"],
        )

    def test_send_message_request(self) -> None:
        """Tests that a Client object can send a message request."""
        client = Client(
            [TestClient.hostname, str(TestClient.port_number), "Alice", "create"],
        )
        receiver_name = "John"
        message = "Hello John"

        with socket.socket() as welcoming_socket:
            # Emulate server with welcoming socket
            welcoming_socket.bind((TestClient.hostname, TestClient.port_number))
            welcoming_socket.listen(1)

            # Send message request from the client
            client.send_request(
                CreateRequest(DUMMY_SESSION_TOKEN, receiver_name, message),
                expect_response=False,
            )

            # Accept connection from the client
            connection_socket, _ = welcoming_socket.accept()
            connection_socket.settimeout(1)

            # Receive message request from the client
            with connection_socket:
                packet = connection_socket.recv(4096)

        message_type, session_token, packet = Packet.decode_packet(packet)

        self.assertEqual(MessageType.CREATE, message_type)
        self.assertEqual(DUMMY_SESSION_TOKEN, session_token)

        expected = (receiver_name, message.encode())
        actual = CreateRequest.decode_packet(packet)
        self.assertEqual(expected, actual)
