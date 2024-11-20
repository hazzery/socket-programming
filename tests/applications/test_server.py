"""Server class test suite."""

import unittest

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

    def test_process_register_request_unused_name(self) -> None:
        """Tests that the server correctly registers new users."""
        server = Server([str(TestServer.port_number)])

        username = "John"
        public_key, _ = rsa.newkeys(512)

        packet = RegistrationRequest(username, public_key).to_bytes()

        server.process_registration_request(None, packet)

        self.assertEqual({username: public_key}, server.users)

    def test_process_register_request_used_name(self) -> None:
        """Tests that the server correctly ignores re-registers."""
        server = Server([str(TestServer.port_number)])

        username = "John"
        existing_key, _ = rsa.newkeys(512)
        public_key, _ = rsa.newkeys(512)

        server.users = {username: existing_key}

        packet = RegistrationRequest(username, public_key).to_bytes()

        server.process_registration_request(None, packet)

        self.assertEqual({username: existing_key}, server.users)

    def test_process_login_request_registered_user(self) -> None:
        """Tests that the server correctly responds to login requests."""
        server = Server([str(TestServer.port_number)])

        username = "John"
        public_key, private_key = rsa.newkeys(512)

        server.users = {username: public_key}

        packet = LoginRequest(username).to_bytes()

        response = server.process_login_request(None, packet).to_bytes()

        (encrypted_session_token,) = LoginResponse.decode_packet(response)
        session_token = rsa.decrypt(encrypted_session_token, private_key)

        self.assertEqual(SessionWrapper.SESSION_TOKEN_LENGTH, len(session_token))

    def test_process_login_request_unknown_user(self) -> None:
        """Tests the the server responds correctly to login requests."""
        server = Server([str(TestServer.port_number)])

        username = "John"

        packet = LoginRequest(username).to_bytes()

        response_packet = server.process_login_request(None, packet).to_bytes()

        (encrypted_session_token,) = LoginResponse.decode_packet(response_packet)

        self.assertEqual(b"", encrypted_session_token)

    def test_process_key_request_registered_user(self) -> None:
        """Tests that the server correctly responds to key request."""
        server = Server([str(TestServer.port_number)])

        receiver_name = "John"
        recipients_key, _ = rsa.newkeys(512)

        server.users = {receiver_name: recipients_key}

        packet = KeyRequest(receiver_name).to_bytes()

        response_packet = server.process_key_request(None, packet).to_bytes()
        (public_key,) = KeyResponse.decode_packet(response_packet)

        self.assertEqual(recipients_key, public_key)

    def test_process_key_request_unknown_user(self) -> None:
        """Tests that the server correctly responds to key request."""
        server = Server([str(TestServer.port_number)])

        receiver_name = "John"

        packet = KeyRequest(receiver_name).to_bytes()

        response_packet = server.process_key_request(None, packet).to_bytes()
        (public_key,) = KeyResponse.decode_packet(response_packet)

        self.assertEqual(None, public_key)

    def test_process_create_request_authorised(self) -> None:
        """Tests that the server correctly stores messages in create requests."""
        server = Server([str(TestServer.port_number)])

        sender_name = "Alice"
        receiver_name = "John"
        message = b"Hello John"

        packet = CreateRequest(receiver_name, message).to_bytes()

        server.process_create_request(sender_name, packet)

        self.assertEqual(
            [(sender_name, message)],
            server.messages[receiver_name],
        )

    def test_process_create_request_unauthorised(self) -> None:
        """Tests that the server ignores messages in unauthorised create requests."""
        server = Server([str(TestServer.port_number)])

        receiver_name = "John"
        message = b"Hello John"

        packet = CreateRequest(receiver_name, message).to_bytes()

        server.process_create_request(None, packet)

        self.assertEqual(None, server.messages.get(receiver_name, None))

    def test_process_read_request_authorised(self) -> None:
        """Tests that the server correctly responds to authorised read requests."""
        server = Server([str(TestServer.port_number)])

        sender_name = "Alice"
        receiver_name = "John"
        message = b"Hello John"

        server.messages[receiver_name] = [(sender_name, message)]

        packet = ReadRequest().to_bytes()

        response_packet = server.process_read_request(receiver_name, packet).to_bytes()

        messages, more_messages = ReadResponse.decode_packet(response_packet)

        self.assertEqual([(sender_name, message)], messages)
        self.assertEqual(False, more_messages)

    def test_process_read_request_unauthorised(self) -> None:
        """Tests that the server responds correctly to unauthorised read reqeusts."""
        server = Server([str(TestServer.port_number)])

        sender_name = "Alice"
        receiver_name = "John"
        message = b"Hello John"

        server.messages[receiver_name] = [(sender_name, message)]

        packet = ReadRequest().to_bytes()

        response_packet = server.process_read_request(None, packet).to_bytes()

        messages, more_messages = ReadResponse.decode_packet(response_packet)

        self.assertEqual([], messages)
        self.assertEqual(False, more_messages)
