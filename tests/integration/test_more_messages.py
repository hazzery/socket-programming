"""More messages functionality test suite."""

import pathlib
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
    that the client is informed they did not receive all of the
    available messages.
    """

    HOST_NAME = "localhost"
    PORT_NUMBER = "1024"
    RECIPIENT_NAME = "Recipient"

    def test_more_messages(self) -> None:
        """Tests that no more than 255 messages are sent in a read request."""
        names = pathlib.Path("tests/resources/names.txt").read_text().splitlines()

        self.assertEqual(MAXIMUM_MESSAGES_PER_RESPONSE + 1, len(names))

        server_object = server.Server([self.PORT_NUMBER])
        server_thread = threading.Thread(target=server_object.run)
        server_thread.start()

        recipient_client = client.Client(
            [self.HOST_NAME, self.PORT_NUMBER, self.RECIPIENT_NAME],
        )
        recipient_client.send_registration_request()

        for sender_name in names:
            sender_client = client.Client(
                [self.HOST_NAME, self.PORT_NUMBER, sender_name],
            )
            sender_client.send_registration_request()
            sender_client.send_login_request()
            sender_client.send_key_request(self.RECIPIENT_NAME)
            sender_client.send_create_request(self.RECIPIENT_NAME, "Hello")

        recipient_client.send_login_request()
        packet = recipient_client.send_read_request()

        server_object.stop()
        server_thread.join()

        if packet is None:
            self.fail("packet was `None`")

        messages, more_messages = ReadResponse.decode_packet(packet)
        self.assertEqual(MAXIMUM_MESSAGES_PER_RESPONSE, len(messages))
        self.assertTrue(more_messages)


if __name__ == "__main__":
    unittest.main()
