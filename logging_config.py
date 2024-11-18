"""Logging configuration for the project.

Applies formatting and specifies output locations
for all module loggers.
"""

import datetime
import logging
import pathlib
import sys


# pylint: disable=too-few-public-methods
class StdoutHandlerFilter(logging.Filter):
    """Filter to only allow DEBUG and INFO messages to stdout."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Denies messages with level WARNING or higher."""
        return record.levelno < logging.WARNING


# pylint: disable=too-few-public-methods
class PathnameFormatter(logging.Formatter):
    """Formatter that replaces the module name with the path to the module."""

    def format(self, record: logging.LogRecord) -> str:
        """Make the filename clickable in PyCharm."""
        record.pathname = record.name.replace(".", "/") + ".py:" + str(record.lineno)

        # Remove newlines from logs being sent to a file
        record.msg = record.msg.lstrip("\n").replace("\n", " ")
        return super().format(record)


def configure_logging(package_name: str) -> None:
    """Configure logging for the project."""
    file_formatter = PathnameFormatter(
        "%(asctime)s - %(levelname)-8s - %(pathname)-35s - %(message)s",
    )
    file_formatter.datefmt = "%d-%m-%y - %H:%M:%S.%s"

    # ruff: noqa: DTZ005
    file_name = datetime.datetime.now().strftime("%d-%m-%y %H:%M:%S")

    log_folder = pathlib.Path("logs") / package_name
    log_folder.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_folder / (file_name + ".log"))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    console_formatter = logging.Formatter("%(message)s")

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.addFilter(StdoutHandlerFilter())
    stdout_handler.setFormatter(console_formatter)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(console_formatter)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[stdout_handler, stderr_handler, file_handler],
    )
