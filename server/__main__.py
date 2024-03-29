"""
Server side program
Run with `python3 -m server <port number>`
"""

import logging
import sys

from logging_config import configure_logging
from .server import Server


logger = logging.getLogger(__name__)


def main() -> None:
    """
    Runs the server side of the program
    """
    configure_logging("server")

    try:
        server = Server(sys.argv[1:])
        server.run()
    except SystemExit:
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server shut down due to keyboard interrupt")
        print("Server shut down")
        sys.exit(0)


if __name__ == "__main__":
    main()
