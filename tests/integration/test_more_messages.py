"""Test suite for the more_messages functionality.

When a client makes a read request to the server and has more than
255 unread messages, the server should only send the first 255. The
server should set the ``more_messages`` flag in the read response so
that the client is informed they did not receive all available messages.
"""

import pathlib
import socket
import sys
import threading

import pytest

sys.path.insert(0, "../../")
import client
import server
from src.packets.read_response import ReadResponse

MAXIMUM_MESSAGES_PER_RESPONSE = 255
HOST_NAME = "localhost"
PORT_NUMBER = "1024"
RECIPIENT_NAME = "Recipient"


@pytest.mark.skip  # type: ignore[misc]
def test_more_messages() -> None:
    """Tests that no more than 255 messages are sent in a read request."""
    names = pathlib.Path("tests/resources/names.txt").read_text().splitlines()

    assert len(set(names)) == MAXIMUM_MESSAGES_PER_RESPONSE + 1

    server_object = server.Server([HOST_NAME, PORT_NUMBER])

    unencrypted_socket = socket.create_server(
        (HOST_NAME, int(PORT_NUMBER)),
    )

    server_thread = threading.Thread(
        target=server_object.run,
        kwargs={"welcoming_socket": unencrypted_socket},
    )
    server_thread.start()

    recipient_client = client.Client(
        [HOST_NAME, PORT_NUMBER, RECIPIENT_NAME],
        connection_socket=socket.create_connection(
            (HOST_NAME, int(PORT_NUMBER)),
        ),
    )
    recipient_client.send_registration_request()

    for sender_name in names:
        sender_client = client.Client(
            [HOST_NAME, PORT_NUMBER, sender_name],
            connection_socket=socket.create_connection(
                (HOST_NAME, int(PORT_NUMBER)),
            ),
        )
        sender_client.send_registration_request()
        sender_client.send_login_request()
        sender_client.send_key_request(RECIPIENT_NAME)
        sender_client.send_create_request(RECIPIENT_NAME, "Hello")

    recipient_client.send_login_request()
    first_packet = recipient_client.send_read_request()
    second_packet = recipient_client.send_read_request()

    server_object.stop()
    server_thread.join()

    assert first_packet is not None
    assert second_packet is not None

    messages, more_messages = ReadResponse.decode_packet(first_packet)
    assert len(messages) == MAXIMUM_MESSAGES_PER_RESPONSE
    assert more_messages is True

    messages, more_messages = ReadResponse.decode_packet(second_packet)
    assert len(messages) == 1
    assert more_messages is False
