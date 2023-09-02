class PortNumber(int):

    MINIMUM = 1024
    MAXIMUM = 64000

    def __new__(cls, string: str):
        try:
            value = int(string)
        except ValueError:
            raise TypeError("Port number must be an integer")

        if not (cls.MINIMUM <= value <= cls.MAXIMUM):
            raise ValueError("Port number must be in the range 1024-64000 (inclusive)")

        return super(cls, cls).__new__(cls, value)
