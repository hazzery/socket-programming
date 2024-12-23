"""Message type enum class test suite."""

import pytest

from src.message_type import MessageType


@pytest.mark.parametrize(  # type: ignore[misc]
    ("test_input", "expected_output"),
    [
        ("read", MessageType.READ),
        ("READ", MessageType.READ),
        ("cReaTe", MessageType.CREATE),
        ("LOGIN", MessageType.LOGIN),
    ],
)
def test_read_lowercase(test_input: str, expected_output: MessageType) -> None:
    """Test that read is parsed correctly."""
    assert MessageType.from_str(test_input) == expected_output


def test_invalid() -> None:
    """Test that invalid input raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid message type: .*"):
        MessageType.from_str("invalid")
