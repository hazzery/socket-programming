"""MessageResponse class test suite."""

from src.packets.read_response import ReadResponse


def test_num_messages_encoding() -> None:
    """Tests that the number of messages is encoded correctly."""
    messages = [
        ("Harry", b"Hello John!"),
        ("John", b"Hello Harry!"),
    ]
    packet = ReadResponse(messages).to_bytes()

    expected = len(messages)
    actual = packet[0]
    assert expected == actual


def test_more_messages_encoding() -> None:
    """Tests that the more messages flag is encoded correctly."""
    messages: list[tuple[str, bytes]] = []
    packet = ReadResponse(messages).to_bytes()

    expected = False
    actual = packet[1]
    assert expected == actual


def test_messages_decoding() -> None:
    """Tests that the messages are decoded correctly."""
    messages = [
        ("Harry", b"Hello John!"),
        ("John", b"Hello Harry!"),
    ]
    packet = ReadResponse(messages).to_bytes()

    actual = ReadResponse.decode_packet(packet)[0]
    assert messages == actual


def test_more_messages_decoding_false() -> None:
    """Tests that the more messages flag is decoded correctly."""
    messages = [
        ("Harry", b"Hello John!"),
        ("John", b"Hello Harry!"),
    ]
    packet = ReadResponse(messages).to_bytes()

    expected = False
    actual = ReadResponse.decode_packet(packet)[1]
    assert expected == actual


def test_more_messages_decoding_true() -> None:
    """Tests that the more messages flag is decoded correctly."""
    messages = [("Harry", b"Hello John!")] * 256
    packet = ReadResponse(messages).to_bytes()

    expected = True
    actual = ReadResponse.decode_packet(packet)[1]
    assert expected == actual
