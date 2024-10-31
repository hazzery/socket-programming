"""Home to the ``MessageType``."""

from enum import Enum


class MessageType(Enum):
    """An enum for message types."""

    READ = 1
    CREATE = 2
    RESPONSE = 3
    LOGIN = 4

    @staticmethod
    def from_str(string: str) -> "MessageType":
        """Convert a string to a message type.

        :param string: The string to convert.
        :return: The message type.
        """
        try:
            return MessageType[string.upper()]
        except KeyError as error:
            message = f'Invalid message type: {string}, must be "read" or "create"'
            raise ValueError(message) from error
