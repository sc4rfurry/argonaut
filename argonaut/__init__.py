# /usr/bin/env python3
# -*- coding: utf-8 -*-
from .core import Argonaut, SubCommand
from .arguments import Argument, ArgumentGroup, MutuallyExclusiveGroup
from .decorators import (
    env_var,
    dynamic_default,
    custom_validator,
    type_converter,
    choices,
    custom_action,
    mutually_exclusive,
    argument_group,
)
from .exceptions import (
    ArgonautError,
    ArgonautValidationError,
    ArgonautTypeError,
    ArgonautValueError,
    ArgonautUnknownArgumentError,
    RateLimitError,
    PluginError,
    ConfigurationError,
    ParsingError,
    EnvironmentVariableError,
    InteractiveModeError,
    ArgonautConflictError,
    ArgonautDependencyError,
    PluginLoadError,
    PluginExecutionError,
)
from .shell_completion import generate_completion_script
from .logging import ArgonautLogger, LogLevel
from .plugins import PluginManager, Plugin, PluginMetadata, PluginContext
from .input_sanitizer import sanitize_input
from .fancy_output import ProgressBar, ColoredOutput
from .utils import get_input_with_autocomplete


__all__ = [
    "Argonaut",
    "SubCommand",
    "Argument",
    "ArgumentGroup",
    "MutuallyExclusiveGroup",
    "env_var",
    "dynamic_default",
    "custom_validator",
    "type_converter",
    "choices",
    "custom_action",
    "mutually_exclusive",
    "argument_group",
    "ArgonautError",
    "ArgonautValidationError",
    "ArgonautTypeError",
    "ArgonautValueError",
    "ArgonautUnknownArgumentError",
    "RateLimitError",
    "PluginError",
    "ConfigurationError",
    "ParsingError",
    "EnvironmentVariableError",
    "InteractiveModeError",
    "ArgonautConflictError",
    "ArgonautDependencyError",
    "PluginLoadError",
    "PluginExecutionError",
    "generate_completion_script",
    "ArgonautLogger",
    "LogLevel",
    "PluginManager",
    "Plugin",
    "PluginMetadata",
    "sanitize_input",
    "ProgressBar",
    "ColoredOutput",
    "get_input_with_autocomplete",
    "PluginContext",
]

__version__ = "1.2.0"
