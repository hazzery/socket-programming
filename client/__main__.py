"""Client side program.

Run with ``python3 -m client <host name> <port number> <username>``
"""

import argparse
import sys

from logging_config import configure_logging
from src.parse_hostname import parse_hostname
from src.parse_username import parse_username
from src.port_number import PortNumber

from .client import Client


def configure_cli() -> argparse.Namespace:
    """Configure command line arguments."""
    argument_parser = argparse.ArgumentParser(
        "Client",
        description="Open a client to communicate to the server",
    )

    argument_parser.add_argument(
        "hostname",
        help=(
            "The address the server is running on. "
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
        "username",
        help="The name of the user to connect to the server as",
        type=parse_username,
    )
    argument_parser.add_argument(
        "--certificate",
        "-c",
        help="Path to the server's SSL certificate (PEM encoding)",
        default="server_cert.pem",
    )

    return argument_parser.parse_args()


def main() -> None:
    """Run the client side of the program."""
    configure_logging("client")

    arguments = configure_cli()

    try:
        client = Client(arguments.hostname, arguments.port_number, arguments.username)
        client.run()
    except SystemExit:
        sys.exit(1)


if __name__ == "__main__":
    main()
