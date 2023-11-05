"""
Server side program
Run with `python3 server.py <port number>`
"""
from datetime import datetime
import logging
import sys
import os

from src.applications.server import Server


def main() -> None:
    """
    Runs the server side of the program
    """
    os.makedirs(os.path.dirname("logs/server/"), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        filename=f"logs/server/{datetime.now()}.log",
        format="%(asctime)s - %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    try:
        server = Server(sys.argv[1:])
        server.run()
    except SystemExit:
        sys.exit(1)
    except KeyboardInterrupt:
        print("Server shut down")
        sys.exit(0)


if __name__ == "__main__":
    main()
