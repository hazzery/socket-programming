"""Client class test suite."""

import socket
import unittest

from client import Client
from src.message_type import MessageType
from src.packets.create_request import CreateRequest
from src.packets.session_wrapper import SessionWrapper
from src.packets.type_wrapper import TypeWrapper

DUMMY_SESSION_TOKEN = b"01234567890123456789012345678901"


class TestClient(unittest.TestCase):
    """Test suite for Client class."""

    hostname = "localhost"
    port_number = 12000

    def test_construction(self) -> None:
        """Tests that a Client object can be constructed given correct arguments."""
        Client([TestClient.hostname, str(TestClient.port_number), "Alice"])

    def test_construction_raise_error(self) -> None:
        """Tests that a Client object cannot be constructed given invalid arguments."""
        self.assertRaises(
            SystemExit,
            Client,
            ["invalid", str(TestClient.port_number), "Alice", "create"],
        )

    def test_send_create_request(self) -> None:
        """Tests that a Client object can send a create request."""
        client = Client(
            [TestClient.hostname, str(TestClient.port_number), "Alice"],
        )
        receiver_name = "John"
        message = "Hello John"

        with socket.socket() as welcoming_socket:
            # Emulate server with welcoming socket
            welcoming_socket.bind((TestClient.hostname, TestClient.port_number))
            welcoming_socket.listen(1)

            client.session_token = DUMMY_SESSION_TOKEN

            # Send message request from the client
            client.send_create_request(receiver_name, message)

            # Accept connection from the client
            connection_socket, _ = welcoming_socket.accept()
            connection_socket.settimeout(1)

            # Receive message request from the client
            with connection_socket:
                packet = connection_socket.recv(4096)

        message_type, packet = TypeWrapper.decode_packet(packet)
        session_token, packet = SessionWrapper.decode_packet(packet)

        self.assertEqual(MessageType.CREATE, message_type)
        self.assertEqual(DUMMY_SESSION_TOKEN, session_token)

        expected = (receiver_name, message.encode())
        actual = CreateRequest.decode_packet(packet)
        self.assertEqual(expected, actual)
