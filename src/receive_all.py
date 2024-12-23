"""Common socket operations used in client and server."""

import socket


def receive_all(sock: socket.socket, buffer_size_bytes: int) -> bytes:
    """Receive all available data from the given socket.

    :param sock: The socket to read from.
    :param buffer_size_bytes: The size of the buffer to write data to.

    :return: The data received from the socket.
    """
    response_packet = b""
    done = False
    while not done:
        # Note: This order of operations is very important!
        # An additional call to `recv` when there is no data to
        # receive will result in a `TimeoutError`.
        received_bytes = sock.recv(buffer_size_bytes)
        response_packet += received_bytes
        done = len(received_bytes) < buffer_size_bytes

    return response_packet
