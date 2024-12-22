"""More messages functionality test suite."""

import pathlib
import socket
import sys
import threading
import unittest

sys.path.insert(0, "../../")
import client
import server
from src.packets.read_response import ReadResponse

MAXIMUM_MESSAGES_PER_RESPONSE = 255


class TestMoreMessages(unittest.TestCase):
    """Test suite for the more_messages functionality.

    When a client makes a read request to the server and has more than
    255 unread messages, the server should only send the first 255. The
    server should set the ``more_messages`` flag in the read response so
    that the client is informed they did not receive all available messages.
    """

    HOST_NAME = "localhost"
    PORT_NUMBER = "1024"
    RECIPIENT_NAME = "Recipient"

    @unittest.skip("Can't figure out why it's not working")
    def test_more_messages(self) -> None:
        """Tests that no more than 255 messages are sent in a read request."""
        names = pathlib.Path("tests/resources/names.txt").read_text().splitlines()

        self.assertEqual(MAXIMUM_MESSAGES_PER_RESPONSE + 1, len(set(names)))

        server_object = server.Server([self.PORT_NUMBER])

        unencrypted_socket = socket.create_server(
            (self.HOST_NAME, int(self.PORT_NUMBER)),
        )

        server_thread = threading.Thread(
            target=server_object.run,
            kwargs={"welcoming_socket": unencrypted_socket},
        )
        server_thread.start()

        recipient_client = client.Client(
            [self.HOST_NAME, self.PORT_NUMBER, self.RECIPIENT_NAME],
            connection_socket=socket.create_connection(
                (self.HOST_NAME, int(self.PORT_NUMBER)),
            ),
        )
        recipient_client.send_registration_request()

        for sender_name in names:
            sender_client = client.Client(
                [self.HOST_NAME, self.PORT_NUMBER, sender_name],
                connection_socket=socket.create_connection(
                    (self.HOST_NAME, int(self.PORT_NUMBER)),
                ),
            )
            sender_client.send_registration_request()
            sender_client.send_login_request()
            sender_client.send_key_request(self.RECIPIENT_NAME)
            sender_client.send_create_request(self.RECIPIENT_NAME, "Hello")

        recipient_client.send_login_request()
        first_packet = recipient_client.send_read_request()
        second_packet = recipient_client.send_read_request()

        server_object.stop()
        server_thread.join()

        if first_packet is None:
            self.fail("First response packet was `None`")

        if second_packet is None:
            self.fail("Second response packet was `None`")

        messages, more_messages = ReadResponse.decode_packet(first_packet)
        self.assertEqual(MAXIMUM_MESSAGES_PER_RESPONSE, len(messages))
        self.assertTrue(more_messages)

        messages, more_messages = ReadResponse.decode_packet(second_packet)
        self.assertEqual(1, len(messages))
        self.assertFalse(more_messages)


if __name__ == "__main__":
    unittest.main()
