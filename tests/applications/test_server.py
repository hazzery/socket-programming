"""Server class test suite."""

import unittest

import rsa

from server import Server
from src.message_type import MessageType
from src.packets.create_request import CreateRequest
from src.packets.key_request import KeyRequest
from src.packets.key_response import KeyResponse
from src.packets.login_request import LoginRequest
from src.packets.login_response import LoginResponse
from src.packets.packet import Packet
from src.packets.read_request import ReadRequest
from src.packets.read_response import ReadResponse
from src.packets.registration_request import RegistrationRequest

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
        _, _, packet = Packet.decode_packet(packet)

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
        _, _, packet = Packet.decode_packet(packet)

        server.process_registration_request(None, packet)

        self.assertEqual({username: existing_key}, server.users)

    def test_process_login_request_registered_user(self) -> None:
        """Tests that the server correctly responds to login requests."""
        server = Server([str(TestServer.port_number)])

        username = "John"
        public_key, private_key = rsa.newkeys(512)

        server.users = {username: public_key}

        packet = LoginRequest(username).to_bytes()
        _, _, packet = Packet.decode_packet(packet)

        response = server.process_login_request(None, packet)
        message_type, _, payload = Packet.decode_packet(response)

        (encrypted_session_token,) = LoginResponse.decode_packet(payload)
        session_token = rsa.decrypt(encrypted_session_token, private_key)

        self.assertEqual(MessageType.LOGIN_RESPONSE, message_type)
        self.assertEqual(Packet.SESSION_TOKEN_LENGTH, len(session_token))

    def test_process_login_request_unknown_user(self) -> None:
        """Tests the the server responds correctly to login requests."""
        server = Server([str(TestServer.port_number)])

        username = "John"

        packet = LoginRequest(username).to_bytes()
        _, _, packet = Packet.decode_packet(packet)

        response = server.process_login_request(None, packet)
        message_type, session_token, payload = Packet.decode_packet(response)

        (encrypted_session_token,) = LoginResponse.decode_packet(payload)

        self.assertEqual(MessageType.LOGIN_RESPONSE, message_type)
        self.assertEqual(None, session_token)
        self.assertEqual(b"", encrypted_session_token)

    def test_process_key_request_registered_user(self) -> None:
        """Tests that the server correctly responds to key request."""
        server = Server([str(TestServer.port_number)])

        receiver_name = "John"
        recipients_key, _ = rsa.newkeys(512)

        server.users = {receiver_name: recipients_key}

        packet = KeyRequest(receiver_name).to_bytes()
        _, _, packet = Packet.decode_packet(packet)

        response = server.process_key_request(None, packet)
        message_type, session_token, payload = Packet.decode_packet(response)
        (public_key,) = KeyResponse.decode_packet(payload)

        self.assertEqual(MessageType.KEY_RESPONSE, message_type)
        self.assertEqual(None, session_token)
        self.assertEqual(recipients_key, public_key)

    def test_process_key_request_unknown_user(self) -> None:
        """Tests that the server correctly responds to key request."""
        server = Server([str(TestServer.port_number)])

        receiver_name = "John"

        packet = KeyRequest(receiver_name).to_bytes()
        _, _, packet = Packet.decode_packet(packet)

        response = server.process_key_request(None, packet)
        message_type, session_token, payload = Packet.decode_packet(response)
        (public_key,) = KeyResponse.decode_packet(payload)

        self.assertEqual(MessageType.KEY_RESPONSE, message_type)
        self.assertEqual(None, session_token)
        self.assertEqual(None, public_key)

    def test_process_create_request_authorised(self) -> None:
        """Tests that the server correctly stores messages in create requests."""
        server = Server([str(TestServer.port_number)])

        sender_name = "Alice"
        receiver_name = "John"
        message = "Hello John"

        packet = CreateRequest(DUMMY_SESSION_TOKEN, receiver_name, message).to_bytes()
        _, _, packet = Packet.decode_packet(packet)

        server.process_create_request(sender_name, packet)

        self.assertEqual(
            [(sender_name, message.encode())],
            server.messages[receiver_name],
        )

    def test_process_create_request_unauthorised(self) -> None:
        """Tests that the server ignores messages in unauthorised create requests."""
        server = Server([str(TestServer.port_number)])

        receiver_name = "John"
        message = "Hello John"

        packet = CreateRequest(DUMMY_SESSION_TOKEN, receiver_name, message).to_bytes()
        _, _, packet = Packet.decode_packet(packet)

        server.process_create_request(None, packet)

        self.assertEqual(None, server.messages.get(receiver_name, None))

    def test_process_read_request_authorised(self) -> None:
        """Tests that the server correctly responds to authorised read requests."""
        server = Server([str(TestServer.port_number)])

        sender_name = "Alice"
        receiver_name = "John"
        message = b"Hello John"

        server.messages[receiver_name] = [(sender_name, message)]

        packet = ReadRequest(DUMMY_SESSION_TOKEN, receiver_name).to_bytes()
        _, _, packet = Packet.decode_packet(packet)

        response = server.process_read_request(receiver_name, packet)
        message_type, session_token, payload = Packet.decode_packet(response)

        messages, more_messages = ReadResponse.decode_packet(payload)

        self.assertEqual(MessageType.READ_RESPONSE, message_type)
        self.assertEqual(None, session_token)
        self.assertEqual([(sender_name, message.decode())], messages)
        self.assertEqual(False, more_messages)

    def test_process_read_request_unauthorised(self) -> None:
        """Tests that the server responds correctly to unauthorised read reqeusts."""
        server = Server([str(TestServer.port_number)])

        sender_name = "Alice"
        receiver_name = "John"
        message = b"Hello John"

        server.messages[receiver_name] = [(sender_name, message)]

        packet = ReadRequest(DUMMY_SESSION_TOKEN, receiver_name).to_bytes()
        _, _, packet = Packet.decode_packet(packet)

        response = server.process_read_request(None, packet)
        message_type, session_token, payload = Packet.decode_packet(response)

        messages, more_messages = ReadResponse.decode_packet(payload)

        self.assertEqual(MessageType.READ_RESPONSE, message_type)
        self.assertEqual(None, session_token)
        self.assertEqual([], messages)
        self.assertEqual(False, more_messages)
