from collections import OrderedDict
from typing import Callable, Any
import logging
import abc


class CommandLineApplication(metaclass=abc.ABCMeta):

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
        return "Usage: python3 %s" % " ".join(self.parameters)

    def parse_arguments(self, arguments: list[str]) -> list[Any]:
        """
        Parses the command line arguments, ensuring they are valid.
        :param arguments: The command line arguments
        """

        parsed_arguments = []
        try:
            if len(arguments) != len(self.parameters):
                raise ValueError(f"Invalid number of arguments, must be {len(arguments)}")

            for argument, (parameter, parser) in zip(arguments, self.parameters.items()):
                argument = parser(argument)
                parsed_arguments.append(argument)
        except (TypeError, ValueError) as error:
            logging.error(error)
            print(self.usage_prompt)
            print(error)
            raise SystemExit

        return parsed_arguments

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError
