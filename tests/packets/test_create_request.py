"""``CreateRequest`` class test suite."""

import struct

import pytest

from src.packets.create_request import CreateRequest

CREATE_PACKET_HEADER_SIZE = struct.calcsize(CreateRequest.struct_format)


def test_receiver_name_length_encoding() -> None:
    """Tests that the length of the receiver's name is encoded correctly."""
    receiver_name = "Jake"
    message = b"Hello, World!"
    packet = CreateRequest(
        receiver_name,
        message,
    ).to_bytes()

    expected = len(receiver_name.encode())
    actual = packet[0]
    assert expected == actual


def test_message_length_encoding() -> None:
    """Tests that the length of the message is encoded correctly."""
    receiver_name = "Jay"
    message = b"Hello, World!"
    packet = CreateRequest(
        receiver_name,
        message,
    ).to_bytes()

    expected = len(message)
    actual = (packet[1] << 8) | (packet[2] & 0xFF)
    assert expected == actual


def test_receiver_name_encoding() -> None:
    """Tests that the receiver's name is encoded correctly."""
    receiver_name = "Jesse"
    message = b"Hello, World!"
    packet = CreateRequest(
        receiver_name,
        message,
    ).to_bytes()

    expected = receiver_name
    actual = packet[
        CREATE_PACKET_HEADER_SIZE : CREATE_PACKET_HEADER_SIZE
        + len(receiver_name.encode())
    ].decode()
    assert expected == actual


def test_message_encoding() -> None:
    """Tests that the message is encoded correctly."""
    receiver_name = "Jimmy"
    message = b"Hello, World!"
    packet = CreateRequest(
        receiver_name,
        message,
    ).to_bytes()

    start_index = CREATE_PACKET_HEADER_SIZE + len(receiver_name.encode())

    expected = message
    actual = packet[start_index : start_index + len(message)]
    assert expected == actual


def test_create_request_decoding() -> None:
    """Tests that the decode function correctly decodes packets."""
    receiver_name = "Jonty"
    message = b"Hello, World!"

    packet = struct.pack(
        CreateRequest.struct_format,
        len(receiver_name.encode()),
        len(message),
    )

    packet += receiver_name.encode()
    packet += message

    decoded_name, decoded_message = CreateRequest.decode_packet(packet)

    assert decoded_name == receiver_name
    assert decoded_message == message


def test_insufficient_receiver_name_length() -> None:
    """Tests that an exception is raised.

    If the length of the receiver's name is zero.
    """
    receiver_name = "Jonty"
    message = b"Hello, World!"

    packet = struct.pack(
        CreateRequest.struct_format,
        0,
        len(message),
    )

    packet += receiver_name.encode()
    packet += message

    with pytest.raises(
        ValueError,
        match="Received create request with insufficient receiver name length",
    ):
        CreateRequest.decode_packet(packet)


def test_insufficient_message_length() -> None:
    """Tests that an exception is raised.

    If the length of the message is zero.
    """
    receiver_name = "Jonty"
    message = b"Hello, World!"

    packet = struct.pack(
        CreateRequest.struct_format,
        len(receiver_name.encode()),
        0,
    )

    packet += receiver_name.encode()
    packet += message

    with pytest.raises(
        ValueError,
        match="Received create request with insufficient message length",
    ):
        CreateRequest.decode_packet(packet)
