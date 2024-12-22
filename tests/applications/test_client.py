"""Client class test suite."""

import socket

import pytest

from client import Client

DUMMY_SESSION_TOKEN = b"01234567890123456789012345678901"
HOSTNAME = "localhost"
PORT_NUMBER = "12000"


def test_construction() -> None:
    """Tests that a Client object can be constructed given correct arguments."""
    Client(
        [HOSTNAME, PORT_NUMBER, "Alice"],
        connection_socket=socket.socket(),
    )


def test_construction_raise_error() -> None:
    """Tests that a Client object cannot be constructed given invalid arguments."""
    with pytest.raises(SystemExit):
        Client(["invalid", PORT_NUMBER, "Alice"])
