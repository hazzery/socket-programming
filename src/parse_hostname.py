"""Host name parsing functionality to be used by server and client."""

import logging
import socket

logger = logging.getLogger(__name__)


def parse_hostname(host_name: str) -> str:
    """Parse the host name, ensuring it is valid.

    :param host_name: String representing the host name.
    :return: String of the host name.
    :raises ValueError: If the host name is invalid.
    """
    try:
        socket.getaddrinfo(host_name, 1024)
    except socket.gaierror as error:
        message = (
            'Invalid host name, must be an IP address, domain name, or "localhost"'
        )
        logger.debug(message, exc_info=True)
        raise ValueError(message) from error

    return host_name
