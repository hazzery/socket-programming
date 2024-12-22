"""Client class test suite."""

import socket
import unittest

from client import Client

DUMMY_SESSION_TOKEN = b"01234567890123456789012345678901"


class TestClient(unittest.TestCase):
    """Test suite for Client class."""

    hostname = "localhost"
    port_number = 12000

    def test_construction(self) -> None:
        """Tests that a Client object can be constructed given correct arguments."""
        Client(
            [TestClient.hostname, str(TestClient.port_number), "Alice"],
            connection_socket=socket.socket(),
        )

    def test_construction_raise_error(self) -> None:
        """Tests that a Client object cannot be constructed given invalid arguments."""
        self.assertRaises(
            SystemExit,
            Client,
            ["invalid", str(TestClient.port_number), "Alice"],
        )
