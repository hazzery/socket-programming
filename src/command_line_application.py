"""Home to the ``CommandLineApplication`` abstract class."""

from collections import OrderedDict
from typing import Callable, Any
import logging
import abc


logger = logging.getLogger(__name__)


class CommandLineApplication(metaclass=abc.ABCMeta):
    """An abstract class for command line applications.

    Implemented by ``Client`` and ``Server``.
    Defines the usage prompt and the method for parsing command line arguments.
    """

    @abc.abstractmethod
    def __init__(self, parameters: OrderedDict[str, Callable[[str], Any]]):
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

    def parse_arguments(self, arguments: list[str]) -> list[Any]:
        """Parse the command line arguments, ensuring they are valid.

        :param arguments: The command line arguments.
        """
        parsed_arguments = []
        try:
            if len(arguments) != len(self.parameters):
                raise ValueError(
                    f"Invalid number of arguments, must be {len(self.parameters)}"
                )

            for argument, parser in zip(arguments, self.parameters.values()):
                parsed_argument = parser(argument)
                parsed_arguments.append(parsed_argument)
        except (TypeError, ValueError) as error:
            logger.error(error)
            print(self.usage_prompt)
            print(error)
            raise SystemExit from error

        return parsed_arguments

    @abc.abstractmethod
    def run(self) -> None:
        """Run the command line application."""
        raise NotImplementedError
