"""More messages functionality test suite."""

import pathlib
import sys
import threading
import unittest

from src.packets.packet import Packet

sys.path.insert(0, "../../")
import client
import server
from src.packets.read_response import ReadResponse


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
    USER_NAME = "John"

    def test_more_messages(self) -> None:
        """Tests that no more than 255 messages are sent in a read request."""
        names = pathlib.Path("tests/resources/names.txt").read_text().splitlines()

        server_object = server.Server([self.PORT_NUMBER])
        server_thread = threading.Thread(target=server_object.run)
        server_thread.start()

        for name in names:
            client.Client(
                [self.HOST_NAME, self.PORT_NUMBER, name, "create"],
            ).run(receiver_name=self.USER_NAME, message="Hello")

        final_client = client.Client(
            [self.HOST_NAME, self.PORT_NUMBER, self.USER_NAME, "read"],
        )
        final_client.run()

        server_object.stop()
        server_thread.join()

        _, packet = Packet.decode_packet(final_client.result)

        messages, more_messages = ReadResponse.decode_packet(packet)
        self.assertEqual(255, len(messages))
        self.assertTrue(more_messages)


if __name__ == "__main__":
    unittest.main()
