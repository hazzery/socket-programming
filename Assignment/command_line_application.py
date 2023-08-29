from collections import OrderedDict
import abc


class CommandLineApplication(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, parameters: OrderedDict[str, type]):
        """
        Initialises the command line application.
        :param parameters: A dictionary containing the parameters for the command line application
        """
        self.parameters = parameters
        self.arguments = None

    @property
    def usage_prompt(self):
        """
        :return: The usage prompt for the command line application
        """
        return "Usage: python3 %s" % " ".join(self.parameters)

    @abc.abstractmethod
    def parse_arguments(self, arguments: list[str]) -> tuple:
        """
        Parses the command line arguments, ensuring they are valid.
        :param arguments: The command line arguments
        """

        if len(arguments) != len(self.parameters):
            print(self.usage_prompt)
            raise ValueError("Invalid number of arguments")

        arguments = []
        for argument, (parameter, parameter_type) in zip(arguments, self.parameters):
            print(argument, parameter, parameter_type)

            try:
                argument = parameter_type(argument)
                arguments.append(argument)
            except ValueError as error:
                # log error
                print(self.usage_prompt)
                raise TypeError(f"{parameter} has invalid type {type(argument)}")

        return tuple(arguments)

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError
