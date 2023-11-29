from datetime import datetime
import logging
import sys
import os


class StdoutHandlerFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno < logging.WARNING


class ConsoleLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        record.pathname = record.name.replace(".", "/") + ".py:" + str(record.lineno)
        return super().format(record)


def configure_logging(package_name: str) -> None:
    file_formatter = logging.Formatter(
        "%(asctime)s - "
        "%(levelname)-8s - "
        "%(name)s %(funcName)s() line:%(lineno)-3d - "
        "%(message)s"
    )
    file_formatter.datefmt = "%d-%m-%y - %H:%M:%S.%s"

    file_name = datetime.now().strftime("%d-%m-%y %H:%M:%S")

    os.makedirs(os.path.dirname(f"logs/{package_name}/"), exist_ok=True)
    file_handler = logging.FileHandler(f"logs/{package_name}/{file_name}.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    console_formatter = ConsoleLogFormatter(
        "%(levelname)-8s - %(pathname)-35s - %(message)s"
    )

    # stdout_handler = logging.StreamHandler(sys.stdout)
    # stdout_handler.setLevel(logging.DEBUG)
    # stdout_handler.addFilter(StdoutHandlerFilter())
    # stdout_handler.setFormatter(console_formatter)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(console_formatter)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, stderr_handler],
    )
