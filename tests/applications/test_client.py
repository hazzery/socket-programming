"""
Client class test suite
"""

import unittest
import socket

from src.packets.message_request import MessageRequest
from src.message_type import MessageType
from client import Client


class TestClient(unittest.TestCase):
    """
    Test suite for Client class
    """

    hostname = "localhost"
    port_number = 12000

    def test_construction(self) -> None:
        """
        Tests that a Client object can be constructed given correct arguments
        """
        Client([TestClient.hostname, str(TestClient.port_number), "Alice", "create"])

    def test_construction_raise_error(self) -> None:
        """
        Tests that a Client object cannot be constructed given an invalid arguments
        """
        self.assertRaises(
            SystemExit,
            Client,
            ["invalid", str(TestClient.port_number), "Alice", "create"],
        )

    def test_send_message_request(self) -> None:
        """
        Tests that a Client object can send a message request
        """
        client = Client(
            [TestClient.hostname, str(TestClient.port_number), "Alice", "create"]
        )
        user_name = "Alice"
        receiver_name = "John"
        message = "Hello John"

        with socket.socket() as welcoming_socket:
            # Emulate server with welcoming socket
            welcoming_socket.bind((TestClient.hostname, TestClient.port_number))
            welcoming_socket.listen(1)

            # Send message request from the client
            client.send_message_request(
                MessageRequest(MessageType.CREATE, user_name, receiver_name, message)
            )

            # Accept connection from the client
            connection_socket, _ = welcoming_socket.accept()
            connection_socket.settimeout(1)

            # Receive message request from the client
            with connection_socket:
                packet = connection_socket.recv(4096)

        # Check that the packet is correct
        request = MessageRequest.decode_packet(packet)
        self.assertEqual(
            (MessageType.CREATE, user_name, receiver_name, message.encode()), request
        )
