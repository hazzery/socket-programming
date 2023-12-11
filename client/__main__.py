"""
Client side program
Run with `python3 -m client <host name> <port number> <username> <message_type>`
"""
import sys

from logging_config import configure_logging
from .client import Client


def main() -> None:
    """
    Runs the client side of the program
    """
    configure_logging("client")

    try:
        client = Client(sys.argv[1:])
        client.run()
    except SystemExit:
        sys.exit(1)


if __name__ == "__main__":
    main()
