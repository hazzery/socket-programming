"""username parsing functionality to be used by client."""

import logging

logger = logging.getLogger(__name__)

MAX_USERNAME_LENGTH = 255


def parse_username(user_name: str) -> str:
    """Parse the username, ensuring it is valid.

    :param user_name: String representing the username.
    :return: String of the username.
    :raises ValueError: If the username is invalid.
    """
    if len(user_name) == 0:
        logger.error("Username is empty")
        raise ValueError("Username must not be empty")

    if len(user_name.encode()) > MAX_USERNAME_LENGTH:
        logger.error("Username consumes more than 255 bytes")
        raise ValueError("Username must consume at most 255 bytes")

    return user_name
