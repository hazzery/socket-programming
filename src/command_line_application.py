"""
This module contains the CommandLineApplication class,
an abstract class for command line applications.

It is implemented by the Client and Server classes.
"""

from collections import OrderedDict
from typing import Callable, Any
import logging
import abc


class CommandLineApplication(metaclass=abc.ABCMeta):
    """
    An abstract class for command line applications.

    Defines the usage prompt and the method for parsing command line arguments.
    """

    @abc.abstractmethod
    def __init__(self, parameters: OrderedDict[str, Callable[[str], Any]]):
        """
        Initialises the command line application.
        :param parameters: A dictionary containing the parameters for the command line application
        """
        self.parameters = parameters

    @property
    def usage_prompt(self) -> str:
        """
        :return: The usage prompt for the command line application
        """
        return f"Usage: python3 {' '.join(self.parameters)}"

    def parse_arguments(self, arguments: list[str]) -> list[Any]:
        """
        Parses the command line arguments, ensuring they are valid.
        :param arguments: The command line arguments
        """
        parsed_arguments = []
        try:
            if len(arguments) != len(self.parameters):
                raise ValueError(f"Invalid number of arguments, must be {len(self.parameters)}")

            for argument, (_, parser) in zip(arguments, self.parameters.items()):
                argument = parser(argument)
                parsed_arguments.append(argument)
        except (TypeError, ValueError) as error:
            logging.error(error)
            print(self.usage_prompt)
            print(error)
            raise SystemExit from error

        return parsed_arguments

    @abc.abstractmethod
    def run(self) -> None:
        """
        Run the command line application.
        """
        raise NotImplementedError
