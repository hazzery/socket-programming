class PortNumber(int):

    def __new__(cls, string: str):
        try:
            value = int(string)
        except ValueError:
            raise TypeError("Port number must be an integer")

        if value not in range(1024, 64001):
            raise ValueError("Port number must be in the range 1024-64000")

        return super(cls, cls).__new__(cls, value)
