# /usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List
import traceback


class ArgonautBaseException(Exception):
    """Base exception for all ArgøNaut exceptions."""

    pass


class ArgonautError(ArgonautBaseException):
    """Base exception for Argonaut errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"ArgonautError: {self.message}"

    def get_formatted_error(self, include_traceback: bool = False) -> str:
        error_msg = f"{self.__class__.__name__}: {self.message}"
        if include_traceback:
            error_msg += (
                f"\n\nTraceback:\n{''.join(traceback.format_tb(self.__traceback__))}"
            )
        return error_msg


class ArgonautValidationError(ArgonautError):
    """Raised when argument validation fails."""

    def __init__(self, argument_name: str, reason: str):
        self.argument_name = argument_name
        self.reason = reason
        message = f"Validation failed for argument '{argument_name}': {reason}"
        super().__init__(message)


class ArgonautTypeError(ArgonautError):
    """Raised when there's a type mismatch in Argonaut configuration."""

    def __init__(self, argument_name: str, expected_type: str, received_type: str):
        self.argument_name = argument_name
        self.expected_type = expected_type
        self.received_type = received_type
        message = f"Type mismatch for argument '{argument_name}': expected {expected_type}, got {received_type}"
        super().__init__(message)


class ArgonautValueError(ArgonautError):
    """Raised when an invalid value is provided for an argument."""

    def __init__(
        self, argument_name: str, invalid_value: str, allowed_values: str = None
    ):
        self.argument_name = argument_name
        self.invalid_value = invalid_value
        self.allowed_values = allowed_values
        message = f"Invalid value '{invalid_value}' for argument '{argument_name}'"
        if allowed_values:
            message += f". Allowed values are: {allowed_values}"
        super().__init__(message)


class ArgonautUnknownArgumentError(ArgonautError):
    """Raised when an unknown argument is provided."""

    def __init__(self, unknown_args: List[str]):
        self.unknown_args = unknown_args
        message = f"Unknown argument(s): {', '.join(unknown_args)}"
        super().__init__(message)


class RateLimitError(ArgonautError):
    """Raised when rate limit is exceeded."""

    def __init__(self, limit: int, period: str):
        self.limit = limit
        self.period = period
        message = f"Rate limit exceeded: {limit} requests per {period}"
        super().__init__(message)


class PluginError(ArgonautError):
    """Raised when there's an error with plugins."""

    def __init__(self, plugin_name: str, error_message: str):
        self.plugin_name = plugin_name
        self.error_message = error_message
        message = f"Error in plugin '{plugin_name}': {error_message}"
        super().__init__(message)

    def __str__(self):
        return f"PluginError in '{self.plugin_name}': {self.error_message}"


class ConfigurationError(ArgonautError):
    """Raised when there's an error in the Argonaut configuration."""

    def __init__(self, config_item: str, error_message: str):
        self.config_item = config_item
        self.error_message = error_message
        message = f"Configuration error in '{config_item}': {error_message}"
        super().__init__(message)


class ParsingError(ArgonautError):
    """Raised when there's an error parsing command-line arguments."""

    def __init__(self, argument: str, error_message: str):
        self.argument = argument
        self.error_message = error_message
        message = f"Error parsing argument '{argument}': {error_message}"
        super().__init__(message)


class EnvironmentVariableError(ArgonautError):
    """Raised when there's an error related to environment variables."""

    def __init__(self, variable_name: str, error_message: str):
        self.variable_name = variable_name
        self.error_message = error_message
        message = f"Environment variable error for '{variable_name}': {error_message}"
        super().__init__(message)


class InteractiveModeError(ArgonautError):
    """Raised when there's an error in interactive mode."""

    def __init__(self, error_message: str):
        self.error_message = error_message
        message = f"Error in interactive mode: {error_message}"
        super().__init__(message)


class ArgonautErrorHandler:
    @staticmethod
    def handle_error(error: ArgonautError, parser: "Argonaut"):
        if isinstance(error, ArgonautUnknownArgumentError):
            print(f"Unknown argument(s): {', '.join(error.unknown_args)}")
            suggestions = parser._suggest_corrections(error.unknown_args)
            if suggestions:
                print("Did you mean one of these?")
                for suggestion in suggestions:
                    print(f"  {suggestion}")
            print("\nTip: Use '--help' to see all available arguments.")
        elif isinstance(error, ArgonautValidationError):
            print(f"Validation error for argument '{error.argument_name}': {error}")
            arg = parser.get_argument(error.argument_name)
            if arg and arg.help:
                print(f"Help for '{error.argument_name}': {arg.help}")
            if arg and arg.choices:
                print(f"Allowed values: {', '.join(map(str, arg.choices))}")
        elif isinstance(error, ArgonautTypeError):
            print(
                f"Type error for argument '{error.argument_name}': Expected {error.expected_type}, got {error.received_type}"
            )
            print(
                f"Tip: Make sure you're providing the correct type of value for this argument."
            )
        elif isinstance(error, PluginError):
            print(f"Plugin error: {error}")
            if isinstance(error, PluginLoadError):
                print(
                    f"Tip: Check if the plugin file exists and is in the correct location."
                )
            elif isinstance(error, PluginExecutionError):
                print(f"Tip: Check the plugin's code for any issues or exceptions.")
        else:
            print(f"Error: {error}")

        print(
            f"\nUse '{parser.prog} --help' for more information on how to use this command."
        )
        if parser.debug:
            print("\nDebug information:")
            print(error.get_formatted_error(include_traceback=True))


class PluginLoadError(PluginError):
    """Raised when there's an error loading a plugin."""

    pass


class ArgumentValidationError(ArgonautError):
    """Raised when argument validation fails."""

    pass


class PluginConfigurationError(ArgonautError):
    """Raised when there's an error in plugin configuration."""

    pass


# Add more specific exception types
class ArgonautParsingError(ArgonautError):
    """Raised when there's a general parsing error."""


class ArgonautMissingArgumentError(ArgonautError):
    """Raised when a required argument is missing."""


class ArgonautInvalidChoiceError(ArgonautError):
    """Raised when an invalid choice is provided for an argument."""


# ... (other specific exception types)


class ArgonautDependencyError(ArgonautError):
    """Raised when a dependency between arguments is not satisfied."""

    pass


class ArgonautConflictError(ArgonautError):
    """Raised when conflicting arguments are provided."""

    pass


# Add these new exception classes
class PluginLoadError(PluginError):
    pass


class PluginExecutionError(PluginError):
    pass
