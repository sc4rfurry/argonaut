import sys
import os
from typing import Any, Dict, List, Optional, Callable, Tuple
from .arguments import Argument, ArgumentGroup, MutuallyExclusiveGroup
from .plugins import PluginManager
from .logging import ArgonautLogger, LogLevel
from .input_sanitizer import sanitize_input
from .fancy_output import ProgressBar, ColoredOutput
from .shell_completion import generate_completion_script
from .exceptions import (
    ArgonautError,
    ArgonautUnknownArgumentError,
    ArgonautValidationError,
)
import secrets
import platform
from difflib import get_close_matches


class SubCommand:
    def __init__(self, name: str, description: str = "", **kwargs):
        self.name = name
        self.description = description
        self.arguments = []
        self.argument_groups = []
        self.exclusive_groups = []
        self.subcommands = {}
        self.parent = kwargs.get("parent")

    def add(self, *names, **kwargs) -> Argument:
        arg = Argument(*names, **kwargs)
        self.arguments.append(arg)
        return arg

    def add_group(self, title: str, description: str = "") -> ArgumentGroup:
        group = ArgumentGroup(title, description)
        self.argument_groups.append(group)
        return group

    def add_exclusive_group(self) -> MutuallyExclusiveGroup:
        group = MutuallyExclusiveGroup()
        self.exclusive_groups.append(group)
        return group

    def add_subcommand(self, name: str, **kwargs) -> "SubCommand":
        subcommand = SubCommand(name, parent=self, **kwargs)
        self.subcommands[name] = subcommand
        return subcommand

    def parse_arguments(self, args: List[str]) -> Dict[str, Any]:
        parsed_args = {"subcommand": self.name}
        i = 0
        while i < len(args):
            arg = sanitize_input(args[i])
            if arg.startswith("--"):
                key = arg[2:]
                argument = next((a for a in self.arguments if a.name == key), None)
                if not argument and self.parent:
                    argument = next(
                        (a for a in self.parent.global_arguments if a.name == key), None
                    )
                if argument:
                    if argument.action == "store_true":
                        parsed_args[key] = True
                    elif argument.nargs:
                        nargs = argument.nargs if isinstance(argument.nargs, int) else 1
                        values = []
                        for j in range(nargs):
                            if i + j + 1 < len(args) and not args[i + j + 1].startswith(
                                "-"
                            ):
                                values.append(sanitize_input(args[i + j + 1]))
                            else:
                                break
                        parsed_args[key] = (
                            values
                            if len(values) > 1 or argument.nargs in ("+", "*")
                            else values[0]
                        )
                        i += len(values)
                    elif i + 1 < len(args) and not args[i + 1].startswith("-"):
                        parsed_args[key] = sanitize_input(args[i + 1])
                        i += 1
                    else:
                        parsed_args[key] = True
                else:
                    raise ArgonautUnknownArgumentError([arg])
            elif arg.startswith("-"):
                for flag in arg[1:]:
                    if flag in [a.name for a in self.arguments] or (
                        self.parent
                        and flag in [a.name for a in self.parent.global_arguments]
                    ):
                        parsed_args[flag] = True
                    else:
                        raise ArgonautUnknownArgumentError([f"-{flag}"])
            else:
                if arg in self.subcommands:
                    return self.subcommands[arg].parse_arguments(args[i + 1 :])
                for argument in self.arguments:
                    if argument.is_positional and argument.name not in parsed_args:
                        parsed_args[argument.name] = arg
                        break
                else:
                    raise ArgonautUnknownArgumentError([arg])
            i += 1

        self._validate_args(parsed_args)
        return parsed_args

    def _validate_args(self, parsed_args: Dict[str, Any]) -> None:
        for group in self.exclusive_groups:
            group.validate(parsed_args)

        for arg in self.arguments + [
            a for g in self.argument_groups for a in g.arguments
        ]:
            if arg.name in parsed_args:
                try:
                    parsed_args[arg.name] = arg.validate(parsed_args[arg.name])
                except Exception as e:
                    raise ArgonautValidationError(arg.name, str(e))
            elif arg.name not in parsed_args:
                if arg.required:
                    raise ArgonautValidationError(
                        arg.name, "Required argument is missing"
                    )
                elif arg.default is not None:
                    parsed_args[arg.name] = arg.get_default()

        # Validate mutually exclusive groups
        for group in self.exclusive_groups:
            found_args = [
                arg.name for arg in group.arguments if arg.name in parsed_args
            ]
            if len(found_args) > 1:
                raise ArgonautValidationError(
                    "mutually_exclusive_group",
                    f"Mutually exclusive arguments: {', '.join(found_args)}",
                )

    def generate_help(self) -> str:
        help_text = f"{self.description}\n\n"
        help_text += f"Usage: {self.name} [options]\n\n"
        help_text += "Options:\n"
        for arg in self.arguments:
            help_text += f"  {', '.join(arg.names):<20} {arg.help}\n"

        for group in self.argument_groups:
            help_text += f"\n{group.title}:\n"
            for arg in group.arguments:
                help_text += f"  {', '.join(arg.names):<20} {arg.help}\n"

        if self.subcommands:
            help_text += "\nSubcommands:\n"
            for name, subcommand in self.subcommands.items():
                help_text += f"  {name:<20} {subcommand.description}\n"

        return help_text

    def get_argument(self, name: str) -> Optional[Argument]:
        for arg in self.arguments:
            if arg.name == name or name in arg.names:
                return arg
        return None


class Argonaut:
    def __init__(
        self,
        description: str = "",
        epilog: str = "",
        custom_help_formatter: Optional[Callable] = None,
    ):
        self.description = description
        self.epilog = epilog
        self.arguments = []
        self.argument_groups = []
        self.exclusive_groups = []
        self.subcommands = {}
        self.logger = ArgonautLogger.get_logger("Argonaut")
        self.colored_output = ColoredOutput()
        self.plugin_manager = PluginManager(self, self.logger, self.colored_output)
        self._parsed_args_cache = None
        self.custom_help_formatter = custom_help_formatter
        self.add(
            "--help", "-h", action="store_true", help="Show this help message and exit"
        )
        self.unknown_args = []
        self.parsed_args: Optional[Dict[str, Any]] = None
        self.subcommand_aliases = {}
        self.global_arguments = []

    def add(self, *names, **kwargs) -> Argument:
        arg = Argument(*names, **kwargs)
        self.arguments.append(arg)
        return arg

    def add_group(self, title: str, description: str = "") -> ArgumentGroup:
        group = ArgumentGroup(title, description)
        self.argument_groups.append(group)
        return group

    def add_subcommand(
        self, name: str, aliases: List[str] = [], **kwargs
    ) -> SubCommand:
        subcommand = SubCommand(name, parent=self, **kwargs)
        self.subcommands[name] = subcommand
        for alias in aliases:
            self.subcommand_aliases[alias] = name
        return subcommand

    def add_mutually_exclusive_group(self) -> MutuallyExclusiveGroup:
        group = MutuallyExclusiveGroup()
        self.exclusive_groups.append(group)
        return group

    def add_global_argument(self, *names, **kwargs) -> Argument:
        arg = Argument(*names, **kwargs)
        self.global_arguments.append(arg)
        return arg

    def parse(
        self, args: Optional[List[str]] = None, ignore_unknown: bool = False
    ) -> Dict[str, Any]:
        if self.parsed_args is None:
            args = args if args is not None else sys.argv[1:]

            parsed_args = {}
            self.unknown_args = []

            try:
                self.logger.info("Parsing arguments")
                i = 0
                while i < len(args):
                    arg = sanitize_input(args[i])
                    if arg in self.subcommands or arg in self.subcommand_aliases:
                        subcommand = (
                            self.subcommands.get(arg)
                            or self.subcommands[self.subcommand_aliases[arg]]
                        )
                        parsed_args["subcommand"] = subcommand.name
                        subcommand_args = subcommand.parse_arguments(args[i + 1 :])
                        parsed_args.update(subcommand_args)
                        break
                    elif arg.startswith("-"):
                        i = self._parse_option(arg, args, i, parsed_args)
                    else:
                        self._parse_positional(arg, parsed_args)
                    i += 1

                self._validate_args(parsed_args)
                self._handle_env_var_defaults(parsed_args)

                self.parsed_args = parsed_args
            except ArgonautError as e:
                self.logger.error(f"Error during argument parsing: {str(e)}")
                raise

            if not ignore_unknown and self.unknown_args:
                self._suggest_corrections(self.unknown_args)
                raise ArgonautUnknownArgumentError(self.unknown_args)

        return self.parsed_args

    def _parse_option(
        self, arg: str, args: List[str], i: int, parsed_args: Dict[str, Any]
    ) -> int:
        key = arg.lstrip("-").replace("-", "_")
        argument = self.get_argument(key) or next(
            (a for a in self.global_arguments if a.name == key), None
        )

        if argument:
            if argument.action == "store_true":
                parsed_args[argument.name] = True
            elif argument.nargs:
                if isinstance(argument.nargs, int):
                    nargs = argument.nargs
                elif argument.nargs == "+":
                    nargs = len(args) - i - 1
                elif argument.nargs == "*":
                    nargs = len(args) - i - 1
                else:
                    nargs = 1

                values = []
                for j in range(nargs):
                    if i + j + 1 < len(args) and not args[i + j + 1].startswith("-"):
                        values.append(sanitize_input(args[i + j + 1]))
                    else:
                        break

                if values:
                    parsed_args[argument.name] = (
                        values
                        if len(values) > 1 or argument.nargs in ("+", "*")
                        else values[0]
                    )
                    i += len(values)
                else:
                    parsed_args[argument.name] = True
            elif i + 1 < len(args) and not args[i + 1].startswith("-"):
                parsed_args[argument.name] = sanitize_input(args[i + 1])
                i += 1
            else:
                parsed_args[argument.name] = True
        else:
            self.unknown_args.append(arg)

        return i

    def _parse_positional(self, arg: str, parsed_args: Dict[str, Any]):
        for argument in self.arguments:
            if argument.is_positional and argument.name not in parsed_args:
                parsed_args[argument.name] = arg
                break
        else:
            self.unknown_args.append(arg)

    def _validate_args(self, parsed_args: Dict[str, Any]) -> None:
        for arg in self.arguments:
            if arg.name in parsed_args:
                try:
                    parsed_args[arg.name] = arg.validate(parsed_args[arg.name])
                except Exception as e:
                    raise ArgonautValidationError(arg.name, str(e))
            elif arg.required:
                raise ArgonautValidationError(arg.name, "Required argument is missing")

        # Validate mutually exclusive groups
        for group in self.exclusive_groups:
            found_args = [
                arg.name for arg in group.arguments if arg.name in parsed_args
            ]
            if len(found_args) > 1:
                raise ArgonautValidationError(
                    "mutually_exclusive_group",
                    f"Mutually exclusive arguments: {', '.join(found_args)}",
                )

    def _handle_env_var_defaults(self, parsed_args: Dict[str, Any]) -> None:
        for arg in self.arguments + [
            a for g in self.argument_groups for a in g.arguments
        ]:
            if arg.name not in parsed_args:
                if arg.env_var:
                    env_value = os.environ.get(arg.env_var)
                    if env_value is not None:
                        parsed_args[arg.name] = arg.validate(env_value)
                if arg.name not in parsed_args and arg.default is not None:
                    parsed_args[arg.name] = arg.get_default()

    def _suggest_corrections(self, unknown_args: List[str]):
        all_args = [
            arg.name.lstrip("-") for arg in self.arguments + self.global_arguments
        ]
        for unknown in unknown_args:
            matches = get_close_matches(unknown.lstrip("-"), all_args, n=1, cutoff=0.6)
            if matches:
                self.logger.warning(
                    f"Did you mean '--{matches[0]}' instead of '{unknown}'?"
                )

    def interactive(self) -> Dict[str, Any]:
        parsed_args = {}
        for arg in self.arguments + [
            a for g in self.argument_groups for a in g.arguments
        ]:
            while True:
                try:
                    value = input(f"{arg.help} ({arg.name}): ")
                    parsed_args[arg.name] = arg.validate(value)
                    break
                except Exception as e:
                    print(f"Invalid input: {str(e)}")
        return parsed_args

    def generate_help(self) -> str:
        if self.custom_help_formatter:
            return self.custom_help_formatter(self)

        help_text = self.colored_output.custom_color(f"{self.description}\n\n", "bold")
        help_text += (
            self.colored_output.custom_color("Usage:", "underline")
            + f" python {sys.argv[0]} [options]\n\n"
        )
        help_text += self.colored_output.custom_color("Options:", "underline") + "\n"

        for arg in self.arguments:
            help_text += (
                self.colored_output.green(f"  {', '.join(arg.names):<20}")
                + f" {arg.help}\n"
            )

        for group in self.argument_groups:
            help_text += f"\n{self.colored_output.yellow(group.title)}:\n"
            for arg in group.arguments:
                help_text += (
                    self.colored_output.green(f"  {', '.join(arg.names):<20}")
                    + f" {arg.help}\n"
                )

        if self.subcommands:
            help_text += f"\n{self.colored_output.underline('Subcommands:')}\n"
            for name, subcommand in self.subcommands.items():
                help_text += (
                    self.colored_output.blue(f"  {name:<20}")
                    + f" {subcommand.description}\n"
                )

        if self.epilog:
            help_text += f"\n{self.epilog}\n"

        return help_text

    def print_help(self) -> None:
        print(self.generate_help())

    def load_plugin(self, module_path: str):
        self.plugin_manager.load_plugin(module_path)

    def unload_plugin(self, name: str):
        self.plugin_manager.unload_plugin(name)

    def initialize_plugins(self):
        self.plugin_manager.initialize_plugins(self)

    def execute_plugin(self, name: str, args: Dict[str, Any]):
        return self.plugin_manager.execute_plugin(name, args)

    def list_plugins(self) -> List[Dict[str, str]]:
        return self.plugin_manager.list_plugins()

    def custom_action(
        self, func: Callable[[Any], Any]
    ) -> Callable[[Argument], Argument]:
        def wrapper(argument: Argument) -> Argument:
            argument.action = func
            return argument

        return wrapper

    def set_log_level(self, level: LogLevel):
        self.logger.set_level(level)

    def add_completion(self, shell: str, directory: Optional[str] = None):
        script = generate_completion_script(shell, self)
        if directory:
            script_path = os.path.join(directory, f".{shell}_completion")
        elif platform.system() == "Windows":
            script_path = os.path.join(
                os.environ.get("USERPROFILE", ""), f".{shell}_completion"
            )
        else:
            script_path = os.path.expanduser(f"~/.{shell}_completion")
        with open(script_path, "w") as f:
            f.write(script)
        self.logger.info(
            f"Completion script for {shell} has been written to {script_path}"
        )
        self.logger.info(f"Add the following line to your shell configuration file:")
        self.logger.info(f"source {script_path}")

    def flag(self, *names, help: str = "") -> Argument:
        return self.add(*names, action="store_true", help=help)

    def option(self, *names, type: type = str, help: str = "") -> Argument:
        return self.add(*names, type=type, help=help)

    def positional(self, name: str, type: type = str, help: str = "") -> Argument:
        return self.add(name, type=type, help=help)

    def version(self, version: str):
        def show_version(args):
            print(version)
            sys.exit(0)

        self.add(
            "--version", action="store_true", help="Show program version"
        ).set_custom_action(show_version)

    def generate_secure_token(self, length: int = 32) -> str:
        return secrets.token_hex(length)

    def show_progress_bar(
        self, total: int, description: str = "Processing"
    ) -> ProgressBar:
        return ProgressBar(total, description)

    def reset(self):
        self.parsed_args = None
        self._parsed_args_cache = None

    def get_argument(self, name: str) -> Optional[Argument]:
        for arg in self.arguments + self.global_arguments:
            if arg.name == name or name in arg.names:
                return arg
        for group in self.argument_groups:
            for arg in group.arguments:
                if arg.name == name or name in arg.names:
                    return arg
        return None

    def set_custom_help_formatter(self, formatter: Callable):
        self.custom_help_formatter = formatter

    def set_color_scheme(self, color_scheme: Dict[str, str]):
        self.colored_output.color_scheme = color_scheme.copy()

    def get_parsed_args(self) -> Optional[Dict[str, Any]]:
        return self.parsed_args

    def add_argument(self, *names, **kwargs) -> Argument:
        return self.add(*names, **kwargs)

    def parse_known_args(
        self, args: Optional[List[str]] = None
    ) -> Tuple[Dict[str, Any], List[str]]:
        self.parse(args)
        return self.parsed_args, self.unknown_args
