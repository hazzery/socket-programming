"""Home to the ``PortNumber`` class."""


class PortNumber(int):
    """Provides functionality to validate a port number.

    Port numbers must be within the range 1024-64000 (inclusive).
    """

    MINIMUM = 1024
    MAXIMUM = 64000

    def __new__(cls, string: str) -> "PortNumber":
        """Validate that new port number is in allowed range.

        :param string: A string to parse as a port number.
        :raises TypeError: If the ``string`` cannot be parsed.
        :raises ValueError: If the number is outside the valid range.
        :return: A new ``PortNumber``.
        """
        try:
            value = int(string)
        except ValueError as error:
            raise TypeError("Port number must be an integer") from error

        if not cls.MINIMUM <= value <= cls.MAXIMUM:
            raise ValueError("Port number must be in the range 1024-64000 (inclusive)")

        return super(cls, cls).__new__(cls, value)
