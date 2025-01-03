"""Server side program.

Run with ``python3 -m server <hostname> <port number> [-c CERTIFICATE] [-k PRIVATEKEY]``
"""

import argparse
import logging
import sys

from logging_config import configure_logging
from src.parse_hostname import parse_hostname
from src.port_number import PortNumber

from .server import Server

logger = logging.getLogger(__name__)


def configure_cli() -> argparse.Namespace:
    """Configure command line arguments."""
    argument_parser = argparse.ArgumentParser(
        "Server",
        description="Run the server on the specified hostname and port_number",
    )

    argument_parser.add_argument(
        "hostname",
        help=(
            "The address to host the server on. "
            'Can be an IPv4 or IPv6 address, a domain name, or "localhost"'
        ),
        type=parse_hostname,
    )
    argument_parser.add_argument(
        "port_number",
        help="The port number for the server to run on",
        type=PortNumber,
    )
    argument_parser.add_argument(
        "--certificate",
        "-c",
        help="Path to a PEM encoded SSL certificate",
        default="server_cert.pem",
    )
    argument_parser.add_argument(
        "--key",
        "-k",
        help="Path to a PEM encoded SSL certificate private key",
        default="server_key.pem",
    )

    return argument_parser.parse_args()


def main() -> None:
    """Boot up the server, ready to accept client requests."""
    configure_logging("server")

    arguments = configure_cli()

    server = Server(arguments.hostname, arguments.port_number)

    try:
        server.run(
            certificate=arguments.certificate,
            key_file=arguments.key,
        )
    except SystemExit:
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server shut down")
        sys.exit(0)


if __name__ == "__main__":
    main()
