# /usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Callable, List, Optional, Union, Dict
import os
from urllib.parse import urlparse


# Import exceptions directly
class ArgonautTypeError(Exception):
    pass


class ArgonautValueError(Exception):
    pass


class ArgonautValidationError(Exception):
    pass


class Argument:
    __slots__ = [
        "names",
        "name",
        "required",
        "default",
        "type",
        "choices",
        "help",
        "is_positional",
        "validator",
        "action",
        "nargs",
        "_dynamic_default",
        "env_var",
        "custom_validators",
        "custom_actions",
        "dependencies",
        "conflicts",
        "is_global",
    ]

    def __init__(self, *names: str, **kwargs):
        self.names: List[str] = list(names)
        self.name: str = self.names[0].lstrip("-").replace("-", "_")
        self.required: bool = kwargs.get("required", False)
        self.default: Any = kwargs.get("default")
        self.type: Optional[Union[Callable, List[Callable], str]] = kwargs.get("type")
        self.choices: Optional[List[Any]] = kwargs.get("choices")
        self.help: str = kwargs.get("help", "")
        self.is_positional: bool = not self.names[0].startswith("-")
        self.validator: Optional[Callable[[Any], bool]] = kwargs.get("validator")
        self.action: Union[str, Callable] = kwargs.get("action", "store")
        self.nargs: Optional[Union[int, str]] = kwargs.get("nargs")
        self._dynamic_default: Optional[Callable[[], Any]] = None
        self.env_var: Optional[str] = kwargs.get("env_var")
        self.custom_validators: List[Callable[[Any], bool]] = []
        self.custom_actions: List[Callable[[Any], Any]] = []
        self.dependencies: List[str] = kwargs.get("dependencies", [])
        self.conflicts: List[str] = kwargs.get("conflicts", [])
        self.is_global: bool = kwargs.get("is_global", False)

        if callable(self.default):
            self._dynamic_default = self.default
            self.default = None

    def validate(self, value: Any) -> Any:
        if value is None:
            if self.required:
                raise ArgonautValidationError(self.name, "Required argument is missing")
            return None

        if self.type:
            if isinstance(self.type, str):
                if self.type == "file_path":
                    if not os.path.exists(value):
                        raise ArgonautValidationError(
                            self.name, f"File not found: {value}"
                        )
                elif self.type == "url":
                    try:
                        result = urlparse(value)
                        if not all([result.scheme, result.netloc]):
                            raise ValueError
                    except ValueError:
                        raise ArgonautValidationError(
                            self.name, f"Invalid URL: {value}"
                        )
            elif callable(self.type):
                try:
                    value = self.type(value)
                except ValueError:
                    raise ArgonautTypeError(
                        self.name, str(self.type), type(value).__name__
                    )
            elif isinstance(self.type, (list, tuple)):
                for t in self.type:
                    try:
                        value = t(value)
                        break
                    except ValueError:
                        continue
                else:
                    raise ArgonautTypeError(
                        self.name, str(self.type), type(value).__name__
                    )

        if self.choices is not None:
            if value not in self.choices:
                raise ArgonautValidationError(
                    self.name, f"Value must be one of {self.choices}"
                )

        for validator in self.custom_validators:
            if not validator(value):
                raise ArgonautValidationError(
                    self.name, f"Failed custom validation for value: {value}"
                )

        if self.validator:
            try:
                if not self.validator(value):
                    raise ArgonautValidationError(
                        self.name, f"Failed custom validation for value: {value}"
                    )
            except Exception as e:
                raise ArgonautValidationError(self.name, str(e))

        return value

    def get_default(self) -> Any:
        if self._dynamic_default:
            return self._dynamic_default()
        return self.default

    def handle_action(self, value: Any) -> Any:
        action_handlers = {
            "store_true": lambda _: True,
            "store_false": lambda _: False,
            "append": lambda v: v if isinstance(v, list) else [v],
            "count": lambda v: v if isinstance(v, int) else 1,
        }
        if callable(self.action):
            return self.action(value)
        return action_handlers.get(self.action, lambda v: v)(value)

    def with_default(self, default_value: Any) -> "Argument":
        new_kwargs = {k: v for k, v in self.__dict__.items() if k != "names"}
        new_kwargs["default"] = default_value
        return Argument(*self.names, **new_kwargs)

    def with_type(self, new_type: Callable) -> "Argument":
        new_kwargs = {k: v for k, v in self.__dict__.items() if k != "names"}
        new_kwargs["type"] = new_type
        return Argument(*self.names, **new_kwargs)

    def with_validator(self, validator: Callable[[Any], bool]) -> "Argument":
        new_kwargs = {k: v for k, v in self.__dict__.items() if k != "names"}
        if self.validator:
            new_kwargs["validator"] = lambda x: self.validator(x) and validator(x)
        else:
            new_kwargs["validator"] = validator
        return Argument(*self.names, **new_kwargs)

    def add_validator(self, validator: Callable[[Any], bool]) -> "Argument":
        self.custom_validators.append(validator)
        return self

    def add_action(self, action: Callable[[Any], Any]) -> "Argument":
        self.custom_actions.append(action)
        return self

    def set_custom_action(self, func: Callable[[Any], Any]) -> "Argument":
        self.action = func
        return self

    def with_custom_type(
        self, type_func: Callable[[str], Any], type_name: str
    ) -> "Argument":
        def custom_type(value: str) -> Any:
            try:
                return type_func(value)
            except ValueError:
                raise ArgonautTypeError(self.name, type_name, value)

        self.type = custom_type
        return self

    def add_conflict(self, *args: str) -> "Argument":
        """Add conflicting arguments."""
        self.conflicts.extend(args)
        return self

    def add_dependency(self, *args: str) -> "Argument":
        """Add dependent arguments."""
        self.dependencies.extend(args)
        return self

    def depends_on(self, *arg_names: str) -> "Argument":
        self.dependencies = arg_names
        return self


class ArgumentGroup:
    def __init__(
        self,
        title: str,
        description: str = "",
        formatter: Optional[Callable[[str], str]] = None,
    ):
        self.title = title
        self.description = description
        self.arguments: List[Argument] = []
        self.formatter = formatter or (lambda x: x)

    def add(self, *args, **kwargs) -> Argument:
        argument = Argument(*args, **kwargs)
        self.arguments.append(argument)
        return argument

    def format_help(self) -> str:
        help_text = f"{self.title}:\n"
        if self.description:
            help_text += f"{self.description}\n"
        for arg in self.arguments:
            help_text += self.formatter(f"  {', '.join(arg.names):<20} {arg.help}\n")
        return help_text

    def add_mutually_exclusive_arguments(self, *args: Argument):
        for arg in args:
            self.arguments.append(arg)
        # Logic to ensure mutual exclusivity during parsing


class MutuallyExclusiveGroup:
    def __init__(self):
        self.arguments: List[Argument] = []

    def add(self, *args, **kwargs) -> Argument:
        argument = Argument(*args, **kwargs)
        self.arguments.append(argument)
        return argument

    def validate(self, parsed_args: Dict[str, Any]) -> None:
        found_args = [
            arg.name
            for arg in self.arguments
            if arg.name in parsed_args and parsed_args[arg.name] is not None
        ]
        if len(found_args) > 1:
            raise ArgonautValidationError(
                "mutually_exclusive_group",
                f"Mutually exclusive arguments: {found_args}",
            )
