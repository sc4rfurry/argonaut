from typing import Any, Callable, List, Optional, Union, Dict
from .exceptions import ArgonautTypeError, ArgonautValueError, ArgonautValidationError


class Argument:
    def __init__(self, *names: str, **kwargs):
        self.names: List[str] = list(names)
        self.name: str = self.names[0].lstrip("-").replace("-", "_")
        self.required: bool = kwargs.get("required", False)
        self.default: Any = kwargs.get("default")
        self.type: Optional[Union[Callable, List[Callable]]] = kwargs.get("type")
        self.choices: Optional[List[Any]] = kwargs.get("choices")
        self.help: str = kwargs.get("help", "")
        self.is_positional: bool = not self.names[0].startswith("-")
        self.validator: Optional[Callable[[Any], bool]] = kwargs.get("validator")
        self.action: Union[str, Callable] = kwargs.get("action", "store")
        self.nargs: Optional[Union[int, str]] = kwargs.get("nargs")
        self._dynamic_default: Optional[Callable[[], Any]] = None
        self.env_var: Optional[str] = kwargs.get("env_var")

        if callable(self.default):
            self._dynamic_default = self.default
            self.default = None

    def validate(self, value: Any) -> Any:
        if self.type:
            try:
                value = self.type(value)
            except ValueError as e:
                raise ArgonautTypeError(self.name, str(self.type), type(value).__name__)

        if self.choices is not None:
            if value not in self.choices:
                raise ArgonautValidationError(
                    self.name, f"Value must be one of {self.choices}"
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
        if callable(self.action):
            return self.action(value)
        elif self.action == "store_true":
            return True
        elif self.action == "store_false":
            return False
        elif self.action == "append":
            return [value] if not isinstance(value, list) else value
        elif self.action == "count":
            return value if isinstance(value, int) else 1
        elif self.action == "store":
            if self.nargs:
                if isinstance(self.nargs, int):
                    if not isinstance(value, list) or len(value) != self.nargs:
                        raise ArgonautValueError(
                            self.name, str(value), f"exactly {self.nargs} arguments"
                        )
                elif self.nargs == "+":
                    if not isinstance(value, list) or len(value) < 1:
                        raise ArgonautValueError(
                            self.name, str(value), "one or more arguments"
                        )
                elif self.nargs == "*":
                    if not isinstance(value, list):
                        value = [value]
            return value
        else:
            return value

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

    def set_custom_action(self, func: Callable[[Any], Any]) -> "Argument":
        self.action = func
        return self


class ArgumentGroup:
    def __init__(self, title: str, description: str = ""):
        self.title = title
        self.description = description
        self.arguments: List[Argument] = []

    def add(self, *args, **kwargs) -> Argument:
        argument = Argument(*args, **kwargs)
        self.arguments.append(argument)
        return argument


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
