"""
Server class test suite
"""
import unittest
import socket

from src.packets.message_response import MessageResponse
from server import Server


class TestServer(unittest.TestCase):
    """
    Test suite for Server class
    """

    port_number = 12000
    hostname = "localhost"

    def test_construction(self) -> None:
        """
        Tests that a Server object can be constructed given correct arguments
        """
        Server([str(TestServer.port_number)])

    def test_construction_raise_error(self) -> None:
        """
        Tests that a Server object cannot be constructed given an invalid arguments
        """
        self.assertRaises(
            SystemExit, Server, [str(TestServer.port_number), "Extra argument"]
        )

    def test_process_read_request(self) -> None:
        """
        Tests that Server objects correctly responds to read requests
        """
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

                with server_connection_socket:
                    server.process_read_request(server_connection_socket, receiver_name)

                # Receive message from server
                packet = client_socket.recv(1024)
                response = MessageResponse.decode_packet(packet)

                # Check that the message is correct
                self.assertEqual(([(sender_name, message.decode())], False), response)
