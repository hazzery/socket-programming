"""Server class test suite."""

import pytest
import rsa

from server import Server
from src.packets.create_request import CreateRequest
from src.packets.key_request import KeyRequest
from src.packets.key_response import KeyResponse
from src.packets.login_request import LoginRequest
from src.packets.login_response import LoginResponse
from src.packets.read_request import ReadRequest
from src.packets.read_response import ReadResponse
from src.packets.registration_request import RegistrationRequest
from src.packets.session_wrapper import SessionWrapper

DUMMY_SESSION_TOKEN = b"01234567890123456789012345678901"
PORT_NUMBER = "12000"
HOSTNAME = "localhost"


def test_construction() -> None:
    """Tests that a Server object can be constructed given correct arguments."""
    Server([HOSTNAME, PORT_NUMBER])


def test_construction_raise_error() -> None:
    """Tests that a Server object cannot be constructed given invalid arguments."""
    with pytest.raises(SystemExit):
        Server([HOSTNAME, PORT_NUMBER, "Extra argument"])


def test_process_register_request_unused_name() -> None:
    """Tests that the server correctly registers new users."""
    server = Server([HOSTNAME, PORT_NUMBER])

    username = "John"
    public_key, _ = rsa.newkeys(512)

    packet = RegistrationRequest(username, public_key).to_bytes()

    server.process_registration_request(None, packet)

    assert server.users == {username: public_key}


def test_process_register_request_used_name() -> None:
    """Tests that the server correctly ignores re-registers."""
    server = Server([HOSTNAME, PORT_NUMBER])

    username = "John"
    existing_key, _ = rsa.newkeys(512)
    public_key, _ = rsa.newkeys(512)

    server.users = {username: existing_key}

    packet = RegistrationRequest(username, public_key).to_bytes()

    server.process_registration_request(None, packet)

    assert server.users == {username: existing_key}


def test_process_login_request_registered_user() -> None:
    """Tests that the server correctly responds to login requests."""
    server = Server([HOSTNAME, PORT_NUMBER])

    username = "John"
    public_key, private_key = rsa.newkeys(512)

    server.users = {username: public_key}

    packet = LoginRequest(username).to_bytes()

    response = server.process_login_request(None, packet).to_bytes()

    (encrypted_session_token,) = LoginResponse.decode_packet(response)
    session_token = rsa.decrypt(encrypted_session_token, private_key)

    assert len(session_token) == SessionWrapper.SESSION_TOKEN_LENGTH


def test_process_login_request_unknown_user() -> None:
    """Tests the the server responds correctly to login requests."""
    server = Server([HOSTNAME, PORT_NUMBER])

    username = "John"

    packet = LoginRequest(username).to_bytes()

    response_packet = server.process_login_request(None, packet).to_bytes()

    (encrypted_session_token,) = LoginResponse.decode_packet(response_packet)

    assert encrypted_session_token == b""


def test_process_key_request_registered_user() -> None:
    """Tests that the server correctly responds to key request."""
    server = Server([HOSTNAME, PORT_NUMBER])

    receiver_name = "John"
    recipients_key, _ = rsa.newkeys(512)

    server.users = {receiver_name: recipients_key}

    packet = KeyRequest(receiver_name).to_bytes()

    response_packet = server.process_key_request(None, packet).to_bytes()
    (public_key,) = KeyResponse.decode_packet(response_packet)

    assert public_key == recipients_key


def test_process_key_request_unknown_user() -> None:
    """Tests that the server correctly responds to key request."""
    server = Server([HOSTNAME, PORT_NUMBER])

    receiver_name = "John"

    packet = KeyRequest(receiver_name).to_bytes()

    response_packet = server.process_key_request(None, packet).to_bytes()
    (public_key,) = KeyResponse.decode_packet(response_packet)

    assert public_key is None


def test_process_create_request_authorised() -> None:
    """Tests that the server correctly stores messages in create requests."""
    server = Server([HOSTNAME, PORT_NUMBER])

    sender_name = "Alice"
    receiver_name = "John"
    message = b"Hello John"

    packet = CreateRequest(receiver_name, message).to_bytes()

    server.process_create_request(sender_name, packet)

    assert server.messages[receiver_name] == [(sender_name, message)]


def test_process_create_request_unauthorised() -> None:
    """Tests that the server ignores messages in unauthorised create requests."""
    server = Server([HOSTNAME, PORT_NUMBER])

    receiver_name = "John"
    message = b"Hello John"

    packet = CreateRequest(receiver_name, message).to_bytes()

    server.process_create_request(None, packet)

    assert server.messages.get(receiver_name, None) is None


def test_process_read_request_authorised() -> None:
    """Tests that the server correctly responds to authorised read requests."""
    server = Server([HOSTNAME, PORT_NUMBER])

    sender_name = "Alice"
    receiver_name = "John"
    message = b"Hello John"

    server.messages[receiver_name] = [(sender_name, message)]

    packet = ReadRequest().to_bytes()

    response_packet = server.process_read_request(receiver_name, packet).to_bytes()

    messages, more_messages = ReadResponse.decode_packet(response_packet)

    assert messages == [(sender_name, message)]
    assert more_messages is False


def test_process_read_request_unauthorised() -> None:
    """Tests that the server responds correctly to unauthorised read reqeusts."""
    server = Server([HOSTNAME, PORT_NUMBER])

    sender_name = "Alice"
    receiver_name = "John"
    message = b"Hello John"

    server.messages[receiver_name] = [(sender_name, message)]

    packet = ReadRequest().to_bytes()

    response_packet = server.process_read_request(None, packet).to_bytes()

    messages, more_messages = ReadResponse.decode_packet(response_packet)

    assert messages == []
    assert more_messages is False
