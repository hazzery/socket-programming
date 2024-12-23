"""Message class test suite."""

from src.packets.message import Message


def test_sender_length_encoding() -> None:
    """Tests that the length of the sender's name is encoded correctly."""
    sender_name = "John"
    message_bytes = b"Hello, World!"
    packet = Message(sender_name, message_bytes).to_bytes()

    expected = len(sender_name.encode())
    actual = packet[0]
    assert expected == actual


def test_message_length_encoding() -> None:
    """Tests that the length of the message is encoded correctly."""
    sender_name = "Jack"
    message_bytes = b"Hello, World!"
    packet = Message(sender_name, message_bytes).to_bytes()

    expected = len(message_bytes)
    actual = (packet[1] << 8) | (packet[2] & 0xFF)
    assert expected == actual


def test_sender_name_encoding() -> None:
    """Tests that the sender's name is encoded correctly."""
    sender_name = "Jacob"
    message_bytes = b"Hello, World!"
    packet = Message(sender_name, message_bytes).to_bytes()

    expected = sender_name
    actual = packet[3 : 3 + len(sender_name.encode())].decode()
    assert expected == actual


def test_message_encoding() -> None:
    """Tests that the message is encoded correctly."""
    sender_name = "James"
    message_bytes = b"Hello, World!"
    packet = Message(sender_name, message_bytes).to_bytes()

    starting_index = 3 + len(sender_name.encode())
    expected = message_bytes.decode()
    actual = packet[starting_index : starting_index + len(message_bytes)].decode()
    assert expected == actual
