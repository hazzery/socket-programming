"""Home to the ``MessageType``."""

import enum


class MessageType(enum.Enum):
    """An enum for message types."""

    REGISTER = enum.auto()
    LOGIN = enum.auto()
    LOGIN_RESPONSE = enum.auto()

    KEY = enum.auto()
    KEY_RESPONSE = enum.auto()
    CREATE = enum.auto()

    READ = enum.auto()
    READ_RESPONSE = enum.auto()
    MESSAGE = enum.auto()

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
