from typing import Any, Callable
from .exceptions import ArgonautTypeError, ArgonautValidationError


def env_var(var_name: str):
    """
    Decorator to specify an environment variable for an argument.

    :param var_name: The name of the environment variable
    :return: Decorator function
    """

    def decorator(argument):
        argument.env_var = var_name
        return argument

    return decorator


def dynamic_default(func: Callable[[], Any]):
    """
    Decorator for specifying a dynamic default value for an argument.

    :param func: A callable that returns the default value
    :return: Decorator function
    """

    def decorator(argument):
        if not callable(func):
            raise ArgonautTypeError("Dynamic default", "callable", type(func).__name__)
        argument._dynamic_default = func
        return argument

    return decorator


def custom_validator(func: Callable[[Any], bool]):
    """
    Decorator for adding a custom validation function to an argument.

    :param func: A callable that takes the argument value and returns a boolean
    :return: Decorator function
    """

    def decorator(argument):
        if not callable(func):
            raise ArgonautTypeError("Custom validator", "callable", type(func).__name__)
        argument.validator = func
        return argument

    return decorator


def type_converter(*types):
    """
    Decorator for specifying multiple possible types for an argument.

    :param types: One or more types or type conversion functions
    :return: Decorator function
    """

    def decorator(argument):
        if not types:
            raise ArgonautTypeError(
                "At least one type must be specified for type conversion"
            )
        argument.type = types
        return argument

    return decorator


def choices(*options):
    """
    Decorator for specifying allowed choices for an argument.

    :param options: Allowed values for the argument
    :return: Decorator function
    """

    def decorator(argument):
        if not options:
            raise ArgonautValidationError("At least one choice must be specified")
        argument.choices = options
        return argument

    return decorator


def custom_action(func: Callable[[Any], Any]):
    """
    Decorator for adding a custom action to an argument.

    :param func: A callable that takes the argument value and returns a processed value
    :return: Decorator function
    """

    def decorator(argument):
        if not callable(func):
            raise ArgonautTypeError("Custom action", "callable", type(func).__name__)
        argument.action = func
        return argument

    return decorator


def mutually_exclusive(*args):
    """
    Decorator for creating a mutually exclusive group of arguments.

    :param args: Names of the arguments to be mutually exclusive
    :return: Decorator function
    """

    def decorator(parser):
        group = parser.add_mutually_exclusive_group()
        for arg_name in args:
            group.add_argument(arg_name)
        return parser

    return decorator


def argument_group(title: str, description: str = ""):
    """
    Decorator for creating an argument group.

    :param title: Title of the argument group
    :param description: Description of the argument group
    :return: Decorator function
    """

    def decorator(parser):
        return parser.add_argument_group(title, description)

    return decorator
