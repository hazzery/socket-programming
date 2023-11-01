"""
Client side program
Run with `python3 client.py <host name> <port number> <username> <message_type>`
"""
from datetime import datetime
import logging
import sys
import os

from src.client import Client


def main() -> None:
    """
    Runs the client side of the program
    """
    os.makedirs(os.path.dirname("logs/client/"), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        filename=f"logs/client/{datetime.now()}.log",
        format="%(levelname)s: %(message)s",
    )

    try:
        client = Client(sys.argv[1:])
        client.run()
    except SystemExit:
        sys.exit(1)


if __name__ == "__main__":
    main()
