"""Server class test suite."""

import socket
import unittest

from server import Server
from src.packets.packet import Packet
from src.packets.read_request import ReadRequest
from src.packets.read_response import ReadResponse


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
        receiver_name = "John"
        sender_name = "Alice"
        message = b"Hello John"
        server.messages[receiver_name] = [(sender_name, message)]

        with socket.socket() as server_welcoming_socket:
            server_welcoming_socket.bind((TestServer.hostname, TestServer.port_number))
            server_welcoming_socket.listen(1)

            with socket.socket() as client_socket:
                client_socket.connect((TestServer.hostname, TestServer.port_number))
                server_connection_socket, _ = server_welcoming_socket.accept()

                packet = ReadRequest(receiver_name).to_bytes()
                _, packet = Packet.decode_packet(packet)

                with server_connection_socket:
                    server.process_read_request(packet, server_connection_socket)

                # Receive message from server
                response_packet = client_socket.recv(1024)
                _, response_packet = Packet.decode_packet(response_packet)
                response = ReadResponse.decode_packet(response_packet)

                # Check that the message is correct
                self.assertEqual(([(sender_name, message.decode())], False), response)
