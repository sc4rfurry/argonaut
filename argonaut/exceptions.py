from typing import List


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
