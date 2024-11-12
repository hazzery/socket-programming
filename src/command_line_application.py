"""Home to the ``CommandLineApplication`` abstract class."""

import abc
import logging
from collections import OrderedDict
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class CommandLineApplication(metaclass=abc.ABCMeta):
    """An abstract class for command line applications.

    Implemented by ``Client`` and ``Server``.
    Defines the usage prompt and the method for parsing command line arguments.
    """

    @abc.abstractmethod
    def __init__(self, parameters: OrderedDict[str, Callable[[str], Any]]) -> None:
        """Initialise the command line application.

        :param parameters: A dictionary containing the parameters for
            the command line application.
        """
        self.parameters = parameters

    @property
    def usage_prompt(self) -> str:
        """Get the command line usage prompt to show user.

        :return: The usage prompt for the command line application.
        """
        return f"Usage: python3 {' '.join(self.parameters)}"

    def parse_arguments(self, arguments: list[str]) -> tuple[Any, ...]:
        """Parse the command line arguments, ensuring they are valid.

        :param arguments: The command line arguments.
        """
        if len(arguments) != len(self.parameters):
            message = f"Invalid number of arguments, must be {len(self.parameters)}"
            print(self.usage_prompt)
            print(message)
            raise SystemExit(message)

        try:
            parsed_arguments = tuple(
                parser(argument)
                for argument, parser in zip(
                    arguments,
                    self.parameters.values(),
                    strict=False,
                )
            )
        except TypeError as error:
            logger.exception("Incorrect arguments")
            print(self.usage_prompt)
            print(error)
            raise SystemExit from error

        return parsed_arguments

    @abc.abstractmethod
    def run(self) -> None:
        """Run the command line application."""
        raise NotImplementedError
