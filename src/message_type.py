"""Home to the ``MessageType``."""

from enum import Enum


class MessageType(Enum):
    """An enum for message types."""

    READ = 1
    CREATE = 2
    RESPONSE = 3
    LOGIN = 4
    REGISTER = 5
    MESSAGE = 6
    KEY_REQUEST = 7
    KEY_RESPONSE = 8

    @staticmethod
    def from_str(string: str) -> "MessageType":
        """Convert a string to a message type.

        :param string: The string to convert.
        :return: The message type.
        """
        try:
            return MessageType[string.upper()]
        except KeyError as error:
            message = f"Invalid message type: {string}"
            raise ValueError(message) from error
