# /usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
from typing import Any, Dict, List, Optional, Callable, Tuple, Union
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
    ConfigurationError,
    ArgonautDependencyError,
    ArgonautConflictError,
)
import secrets
import platform
from difflib import get_close_matches
import json
import yaml
from pathlib import Path
import configparser
import textwrap
import asyncio


# Try to import readline, use a dummy object if not available
try:
    import readline
except ImportError:

    class DummyReadline:
        def set_completer(self, *args, **kwargs):
            pass

        def parse_and_bind(self, *args, **kwargs):
            pass

    readline = DummyReadline()


class SubCommand:
    def __init__(self, name: str, description: str = "", **kwargs: Any):
        self.name: str = name
        self.description: str = description
        self.arguments: List[Argument] = []
        self.argument_groups: List[ArgumentGroup] = []
        self.exclusive_groups: List[MutuallyExclusiveGroup] = []
        self.subcommands: Dict[str, SubCommand] = {}
        self.parent: Optional[Union["Argonaut", "SubCommand"]] = kwargs.get("parent")
        self.custom_parsers: List[Callable[[List[str]], Dict[str, Any]]] = []

    def add(self, *names: str, **kwargs: Any) -> Argument:
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

    def add_subcommand(self, name: str, **kwargs: Any) -> "SubCommand":
        subcommand = SubCommand(name, parent=self, **kwargs)
        self.subcommands[name] = subcommand
        return subcommand

    def add_custom_parser(self, parser: Callable[[List[str]], Dict[str, Any]]):
        self.custom_parsers.append(parser)

    def parse_arguments(self, args: List[str]) -> Dict[str, Any]:
        parsed_args: Dict[str, Any] = {"subcommand": self.name}

        global_args = self.parent._get_global_arguments()
        global_arg_dict = {name: arg for arg in global_args for name in arg.names}

        i = 0
        while i < len(args):
            arg = sanitize_input(args[i])
            if arg in ("--help", "-h", "--debug", "-d"):
                parsed_args[arg.lstrip("-")] = True
            elif arg.startswith("--"):
                key = arg[2:].replace("-", "_")
                argument = self._get_argument(key) or global_arg_dict.get(arg)
                if argument:
                    i = self._parse_option(argument, args, i, parsed_args)
                else:
                    raise ArgonautUnknownArgumentError([arg])
            elif arg.startswith("-") and not self.parent._is_negative_number(arg):
                for flag in arg[1:]:
                    argument = self._get_argument(flag) or global_arg_dict.get(
                        f"-{flag}"
                    )
                    if argument:
                        parsed_args[argument.name] = True
                    else:
                        raise ArgonautUnknownArgumentError([f"-{flag}"])
            else:
                self._parse_positional(arg, parsed_args)
            i += 1

        self._validate_args(parsed_args)
        return parsed_args

    def _parse_option(
        self, argument: Argument, args: List[str], i: int, parsed_args: Dict[str, Any]
    ) -> int:
        if argument.action == "store_true":
            parsed_args[argument.name] = True
        elif argument.nargs:
            parsed_args[argument.name] = self._parse_nargs(argument, args[i + 1 :])
            i += (
                len(parsed_args[argument.name])
                if isinstance(parsed_args[argument.name], list)
                else 1
            )
        elif i + 1 < len(args) and not args[i + 1].startswith("-"):
            parsed_args[argument.name] = args[i + 1]
            i += 1
        else:
            parsed_args[argument.name] = True
        return i

    def _parse_positional(self, arg: str, parsed_args: Dict[str, Any]) -> None:
        for argument in self.arguments:
            if argument.is_positional and argument.name not in parsed_args:
                parsed_args[argument.name] = sanitize_input(arg)
                return
        raise ArgonautUnknownArgumentError([arg])

    def _parse_nargs(
        self, argument: Argument, args: List[str]
    ) -> Union[str, List[str]]:
        if isinstance(argument.nargs, int):
            nargs = argument.nargs
        elif argument.nargs in ("+", "*"):
            nargs = len(args)
        elif argument.nargs == "?":
            nargs = 1 if args and not args[0].startswith("-") else 0
        else:
            nargs = 1

        values = []
        for i in range(nargs):
            if i < len(args) and not args[i].startswith("-"):
                values.append(sanitize_input(args[i]))
            else:
                break

        if not values and argument.nargs == "+":
            raise ArgonautValidationError(
                argument.name, "At least one value is required"
            )

        if argument.nargs == "?":
            return values[0] if values else None
        return (
            values
            if len(values) > 1 or argument.nargs in ("+", "*")
            else values[0] if values else None
        )

    def _validate_args(self, parsed_args: Dict[str, Any]) -> None:
        for arg in self.arguments:
            if arg.name in parsed_args:
                try:
                    parsed_args[arg.name] = arg.validate(parsed_args[arg.name])
                except Exception as e:
                    raise ArgonautValidationError(arg.name, str(e))
            elif arg.required:
                raise ArgonautValidationError(arg.name, "Required argument is missing")

        for group in self.exclusive_groups:
            group.validate(parsed_args)

    def _get_argument(self, name: str) -> Optional[Argument]:
        for arg in self.arguments:
            if arg.name == name or name in arg.names:
                return arg
        for group in self.argument_groups:
            for arg in group.arguments:
                if arg.name == name or name in arg.names:
                    return arg
        for group in self.exclusive_groups:
            for arg in group.arguments:
                if arg.name == name or name in arg.names:
                    return arg
        return None

    def generate_help(self) -> str:
        help_text = f"{self.description}\n\n"
        help_text += f"Usage: {self._get_full_command()} [options]\n\n"
        help_text += "Options:\n"
        for arg in self.arguments:
            help_text += f"  {', '.join(arg.names):<20} {arg.help}\n"

        if self.subcommands:
            help_text += "\nSubcommands:\n"
            for name, subcommand in self.subcommands.items():
                help_text += f"  {name:<20} {subcommand.description}\n"

        help_text += f"\nUse '{self._get_full_command()} <subcommand> --help' for more information about a subcommand.\n"
        return help_text

    def _get_full_command(self) -> str:
        if isinstance(self.parent, SubCommand):
            return f"{self.parent._get_full_command()} {self.name}"
        return f"{self.parent.prog} {self.name}"

    def print_help(self):
        help_text = self.generate_help()
        print(help_text)


class Argonaut:
    def __init__(
        self,
        description: str = "",
        epilog: str = "",
        custom_help_formatter: Optional[Callable] = None,
    ):
        self.description: str = description
        self.epilog: str = epilog
        self.arguments: List[Argument] = []
        self.argument_groups: List[ArgumentGroup] = []
        self.exclusive_groups: List[MutuallyExclusiveGroup] = []
        self.subcommands: Dict[str, SubCommand] = {}
        self.logger: ArgonautLogger = ArgonautLogger.get_logger("Argonaut")
        self.colored_output: ColoredOutput = ColoredOutput()
        self.plugin_manager: PluginManager = PluginManager(
            self, self.logger, self.colored_output
        )
        self._parsed_args_cache: Optional[Dict[str, Any]] = None
        self.custom_help_formatter: Optional[Callable] = custom_help_formatter
        self.add(
            "--help", "-h", action="store_true", help="Show this help message and exit"
        )
        self.unknown_args: List[str] = []
        self.parsed_args: Optional[Dict[str, Any]] = None
        self.subcommand_aliases: Dict[str, str] = {}
        self.global_arguments: List[Argument] = []
        self.config_file: Optional[str] = None
        self.custom_parsers: List[Callable[[List[str]], Dict[str, Any]]] = []
        self.prog: str = os.path.basename(sys.argv[0])
        self.debug = False
        self.add_global_argument(
            "--debug", "-d", action="store_true", help="Enable debug mode"
        )
        self.conflicting_groups: List[set] = []

    def add(self, *names: str, **kwargs: Any) -> Argument:
        arg = Argument(*names, **kwargs)
        self.arguments.append(arg)
        return arg

    def add_group(self, title: str, description: str = "") -> ArgumentGroup:
        group = ArgumentGroup(title, description)
        self.argument_groups.append(group)
        return group

    def add_subcommand(self, name: str, **kwargs: Any) -> SubCommand:
        subcommand = SubCommand(name, parent=self, **kwargs)
        self.subcommands[name] = subcommand
        return subcommand

    def add_mutually_exclusive_group(self) -> MutuallyExclusiveGroup:
        group = MutuallyExclusiveGroup()
        self.exclusive_groups.append(group)
        return group

    def add_global_argument(self, *names: str, **kwargs: Any) -> Argument:
        kwargs["is_global"] = True
        arg = Argument(*names, **kwargs)
        self.global_arguments.append(arg)
        return arg

    def add_custom_parser(self, parser: Callable[[List[str]], Dict[str, Any]]):
        self.custom_parsers.append(parser)

    def _get_global_arguments(self) -> List[Argument]:
        return self.global_arguments + [arg for arg in self.arguments if arg.is_global]

    def _get_all_arguments(self):
        all_args = self.arguments + self.global_arguments
        for group in self.argument_groups:
            all_args.extend(group.arguments)
        for group in self.exclusive_groups:
            all_args.extend(group.arguments)
        return all_args

    def _is_negative_number(self, arg: str) -> bool:
        try:
            float(arg)
            return arg.startswith("-")
        except ValueError:
            return False

    def parse(
        self, args: Optional[List[str]] = None, ignore_unknown: bool = False
    ) -> Dict[str, Any]:
        if args is None:
            args = sys.argv[1:]

        global_args = {}
        remaining_args = []
        all_arguments = self._get_all_arguments()
        arg_dict = {name: arg for arg in all_arguments for name in arg.names}
        subcommand = None

        i = 0
        while i < len(args):
            arg = sanitize_input(args[i])
            if arg in ("--debug", "-d"):
                global_args["debug"] = True
            elif arg in self.subcommands:
                subcommand = self.subcommands[arg]
                global_args["subcommand"] = arg
                remaining_args = args[i + 1 :]
                break
            elif arg in ("--help", "-h"):
                self.print_help()
                sys.exit(0)
            elif arg.startswith("-"):
                argument = arg_dict.get(arg)
                if argument:
                    if argument.action == "store_true":
                        global_args[argument.name] = True
                    elif i + 1 < len(args):
                        if not args[i + 1].startswith("-") or self._is_negative_number(
                            args[i + 1]
                        ):
                            global_args[argument.name] = args[i + 1]
                            i += 1
                        else:
                            global_args[argument.name] = True
                    else:
                        global_args[argument.name] = True
                else:
                    remaining_args.append(arg)
            else:
                remaining_args.append(arg)
            i += 1

        self.set_debug(global_args.get("debug", False))

        if self.debug:
            self.logger.debug(f"Running on {platform.system()} platform")
            self.logger.debug("Parsing arguments")

        if self.parsed_args is None:
            parsed_args: Dict[str, Any] = global_args.copy()
            self.unknown_args = []

            try:
                for parser in self.custom_parsers:
                    custom_parsed = parser(remaining_args)
                    parsed_args.update(custom_parsed)
                    remaining_args = [
                        arg for arg in remaining_args if arg not in custom_parsed
                    ]

                if subcommand:
                    if "--help" in remaining_args or "-h" in remaining_args:
                        subcommand.print_help()
                        sys.exit(0)
                    subcommand_args = subcommand.parse_arguments(remaining_args)
                    parsed_args.update(subcommand_args)
                else:
                    i = 0
                    while i < len(remaining_args):
                        arg = remaining_args[i]
                        if arg in ("--help", "-h"):
                            self.print_help()
                            sys.exit(0)
                        elif arg.startswith("-"):
                            argument = self._get_argument(arg.lstrip("-"))
                            if argument:
                                key = argument.name
                                if argument.action == "store_true":
                                    parsed_args[key] = True
                                elif argument.nargs:
                                    parsed_args[key] = self._parse_nargs(
                                        argument, remaining_args[i + 1 :]
                                    )
                                    i += (
                                        len(parsed_args[key])
                                        if isinstance(parsed_args[key], list)
                                        else 1
                                    )
                                elif i + 1 < len(remaining_args):
                                    if not remaining_args[i + 1].startswith(
                                        "-"
                                    ) or self._is_negative_number(
                                        remaining_args[i + 1]
                                    ):
                                        parsed_args[key] = remaining_args[i + 1]
                                        i += 1
                                    else:
                                        parsed_args[key] = True
                                else:
                                    parsed_args[key] = True
                            else:
                                self.unknown_args.append(arg)
                        elif arg == "--":
                            parsed_args["remaining_args"] = remaining_args[i + 1 :]
                            break
                        else:
                            self._parse_positional(arg, parsed_args)
                        i += 1

                self._validate_args(parsed_args)
                self._validate_conflicts(parsed_args)
                self._validate_dependencies(parsed_args)
                self._handle_env_var_defaults(parsed_args)
                self._handle_config_file(parsed_args)

                self.parsed_args = parsed_args
            except ArgonautError as e:
                if self.debug:
                    self.logger.error(f"Error during argument parsing: {str(e)}")
                raise
            except Exception as e:
                if self.debug:
                    self.logger.error(
                        f"Unexpected error during argument parsing: {str(e)}"
                    )
                raise ArgonautError(f"Unexpected error: {str(e)}")

            if not ignore_unknown and self.unknown_args:
                self._suggest_corrections(self.unknown_args)
                raise ArgonautUnknownArgumentError(self.unknown_args)

        return self.parsed_args

    def _parse_positional(self, arg: str, parsed_args: Dict[str, Any]) -> None:
        for argument in self.arguments:
            if argument.is_positional and argument.name not in parsed_args:
                parsed_args[argument.name] = sanitize_input(arg)
                return
        self.unknown_args.append(arg)

    def _parse_nargs(
        self, argument: Argument, args: List[str]
    ) -> Union[str, List[str]]:
        if isinstance(argument.nargs, int):
            nargs = argument.nargs
        elif argument.nargs in ("+", "*"):
            nargs = len(args)
        elif argument.nargs == "?":
            nargs = 1 if args and not args[0].startswith("-") else 0
        else:
            nargs = 1

        values = []
        for i in range(nargs):
            if i < len(args) and not args[i].startswith("-"):
                values.append(sanitize_input(args[i]))
            else:
                break

        if not values and argument.nargs == "+":
            raise ArgonautValidationError(
                argument.name, "At least one value is required"
            )

        if argument.nargs == "?":
            return values[0] if values else None
        return (
            values
            if len(values) > 1 or argument.nargs in ("+", "*")
            else values[0] if values else None
        )

    def _validate_args(self, parsed_args: Dict[str, Any]) -> None:
        for arg in self.arguments + self.global_arguments:
            if arg.name in parsed_args:
                try:
                    parsed_args[arg.name] = arg.validate(parsed_args[arg.name])
                except Exception as e:
                    raise ArgonautValidationError(arg.name, str(e))
            elif arg.required:
                raise ArgonautValidationError(arg.name, "Required argument is missing")

        for group in self.exclusive_groups:
            group.validate(parsed_args)

    def _validate_conflicts(self, parsed_args: Dict[str, Any]) -> None:
        for group in self.conflicting_groups:
            found = [arg for arg in group if arg in parsed_args]
            if len(found) > 1:
                raise ArgonautConflictError(
                    f"Conflicting arguments: {', '.join(found)}"
                )

    def _validate_dependencies(self, parsed_args: Dict[str, Any]) -> None:
        for arg in self.arguments + self.global_arguments:
            if arg.name in parsed_args and arg.dependencies:
                missing = [dep for dep in arg.dependencies if dep not in parsed_args]
                if missing:
                    raise ArgonautDependencyError(
                        f"Argument '{arg.name}' requires: {', '.join(missing)}"
                    )

    def _handle_env_var_defaults(self, parsed_args: Dict[str, Any]) -> None:
        for arg in self.arguments + self.global_arguments:
            if arg.name not in parsed_args:
                if arg.env_var:
                    env_value = os.environ.get(arg.env_var)
                    if env_value is not None:
                        parsed_args[arg.name] = arg.validate(env_value)
                if arg.name not in parsed_args and arg.default is not None:
                    parsed_args[arg.name] = arg.get_default()

    def _handle_config_file(self, parsed_args: Dict[str, Any]) -> None:
        if self.config_file and os.path.exists(self.config_file):
            config = self._load_config_file(self.config_file)
            for key, value in config.items():
                if key not in parsed_args:
                    arg = self.get_argument(key)
                    if arg:
                        parsed_args[key] = arg.validate(value)

    def _load_config_file(self, config_file: str) -> Dict[str, Any]:
        try:
            with open(config_file, "r") as f:
                if config_file.endswith(".json"):
                    return json.load(f)
                elif config_file.endswith(".yaml") or config_file.endswith(".yml"):
                    return yaml.safe_load(f)
                else:
                    raise ConfigurationError(
                        f"Unsupported config file format: {config_file}"
                    )
        except Exception as e:
            raise ConfigurationError(f"Error loading config file: {str(e)}")

    def _suggest_corrections(self, unknown_args: List[str]) -> List[str]:
        all_args = [arg.name for arg in self.arguments + self.global_arguments]
        suggestions = []
        for unknown in unknown_args:
            matches = get_close_matches(unknown.lstrip("-"), all_args, n=3, cutoff=0.6)
            suggestions.extend(f"--{match}" for match in matches)
        return suggestions

    def _get_argument(self, name: str) -> Optional[Argument]:
        for arg in self.arguments + self.global_arguments:
            if (
                arg.name == name
                or name in arg.names
                or name in [n.lstrip("-") for n in arg.names]
            ):
                return arg
        return None

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
        help_text = self.generate_help()
        print(self.colored_output.custom_color(help_text, "reset"))

    def set_debug(self, debug: bool):
        self.debug = debug
        if self.debug:
            self.logger.set_level(LogLevel.DEBUG)
        else:
            self.logger.set_level(LogLevel.INFO)

    def add_conflicting_group(self, *args: str) -> None:
        """Add a group of mutually conflicting arguments."""
        self.conflicting_groups.append(set(args))

    def interactive(self) -> Dict[str, Any]:
        parsed_args: Dict[str, Any] = {}
        for arg in self.arguments + [
            a for g in self.argument_groups for a in g.arguments
        ]:
            while True:
                try:
                    value = input(f"{arg.help} ({arg.name}): ")
                    parsed_args[arg.name] = arg.validate(value)
                    parsed_args[arg.name] = arg.handle_action(parsed_args[arg.name])
                    break
                except Exception as e:
                    print(f"Invalid input: {str(e)}")
        return parsed_args

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
            script_path = Path(directory) / f".{shell}_completion"
        elif sys.platform == "win32":
            script_path = Path.home() / f".{shell}_completion"
        else:
            script_path = Path.home() / f".{shell}_completion"
        script_path.write_text(script)
        self.logger.info(
            f"Completion script for {shell} has been written to {script_path}"
        )
        self.logger.info(f"Add the following line to your shell configuration file:")
        self.logger.info(f"source {script_path}")

    def flag(self, *names: str, help: str = "") -> Argument:
        return self.add(*names, action="store_true", help=help)

    def option(self, *names: str, type: type = str, help: str = "") -> Argument:
        return self.add(*names, type=type, help=help)

    def positional(self, name: str, type: type = str, help: str = "") -> Argument:
        return self.add(name, type=type, help=help)

    def version(self, version: str):
        def show_version(args: Dict[str, Any]):
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

    def add_argument(self, *names: str, **kwargs: Any) -> Argument:
        return self.add(*names, **kwargs)

    def parse_known_args(
        self, args: Optional[List[str]] = None
    ) -> Tuple[Dict[str, Any], List[str]]:
        self.parse(args)
        return self.parsed_args, self.unknown_args

    def set_config_file(self, config_file: str):
        if not Path(config_file).is_file():
            raise ConfigurationError(f"Config file not found: {config_file}")
        self.config_file = config_file

    def add_subparser(self, name: str, help: str = "") -> "Argonaut":
        subparser = Argonaut(description=help, parent=self)
        self.subcommands[name] = subparser
        return subparser

    def parse_args(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        parsed_args = self.parse(args)
        if "subcommand" in parsed_args:
            subcommand = self.subcommands[parsed_args["subcommand"]]
            sub_args = subcommand.parse_args(
                args[args.index(parsed_args["subcommand"]) + 1 :]
            )
            parsed_args.update(sub_args)
        return parsed_args

    def load_config_files(self, *config_files: str):
        config = configparser.ConfigParser()
        for file in config_files:
            config.read(file)
        self.config = config

    def interactive_input(self):
        def completer(text, state):
            options = [arg.name for arg in self.arguments if arg.name.startswith(text)]
            if state < len(options):
                return options[state]
            else:
                return None

        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

        for arg in self.arguments:
            if arg.name not in self.parsed_args:
                value = input(f"{arg.help} ({arg.name}): ")
                self.parsed_args[arg.name] = arg.validate(value)

    def add_dynamic_argument(self, *names: str, **kwargs: Any) -> Argument:
        arg = Argument(*names, **kwargs)
        self.arguments.append(arg)
        return arg

    def load_config(self, config_file: Union[str, Path]):
        """
        Load arguments from a configuration file.

        Args:
            config_file (Union[str, Path]): Path to the configuration file (YAML or JSON).

        Raises:
            FileNotFoundError: If the config file doesn't exist.
            ValueError: If the config file format is not supported.
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with config_path.open() as f:
            if config_path.suffix in (".yaml", ".yml"):
                config = yaml.safe_load(f)
            elif config_path.suffix == ".json":
                config = json.load(f)
            else:
                raise ValueError(
                    f"Unsupported config file format: {config_path.suffix}"
                )

        for arg_name, arg_value in config.items():
            self.add_dynamic_argument(arg_name, default=arg_value)

    def generate_man_page(self) -> str:
        man_page = f""".TH {self.prog.upper()} 1 "$(date +"%B %Y")" "Version {self.__version__}" "User Commands"
.SH NAME
{self.prog} \\- {self.description}
.SH SYNOPSIS
.B {self.prog}
[OPTIONS]
.SH DESCRIPTION
{textwrap.fill(self.description, width=80)}
.SH OPTIONS
"""
        for arg in self.arguments:
            man_page += f".TP\n.B {', '.join(arg.names)}\n{arg.help}\n"

        return man_page

    def write_man_page(self, filename: str):
        with open(filename, "w") as f:
            f.write(self.generate_man_page())

    def create_argument_group(self, title: str, description: str = "") -> ArgumentGroup:
        group = ArgumentGroup(title, description)
        self.argument_groups.append(group)
        return group

    def create_progress_bar(
        self, total: int, description: str = "Processing"
    ) -> ProgressBar:
        return ProgressBar(total, description)

    async def parse_async(
        self, args: Optional[List[str]] = None, ignore_unknown: bool = False
    ) -> Dict[str, Any]:
        """
        Asynchronous version of the parse method.

        This method allows for asynchronous argument parsing, which can be useful in async applications.
        The actual parsing is still synchronous, but this method can be awaited in an async context.

        Args:
            args (Optional[List[str]]): List of command-line arguments. If None, sys.argv[1:] will be used.
            ignore_unknown (bool): If True, unknown arguments will be ignored instead of raising an error.

        Returns:
            Dict[str, Any]: A dictionary containing the parsed arguments.

        Raises:
            ArgonautUnknownArgumentError: If unknown arguments are encountered and ignore_unknown is False.
            ArgonautError: If an unexpected error occurs during parsing.
        """
        return await asyncio.to_thread(self.parse, args, ignore_unknown)

    async def execute_plugin_async(self, name: str, args: Dict[str, Any]) -> Any:
        """
        Asynchronous version of execute_plugin method.

        This method allows for asynchronous plugin execution, which can be useful in async applications.

        Args:
            name (str): Name of the plugin to execute.
            args (Dict[str, Any]): Arguments to pass to the plugin.

        Returns:
            Any: The result of the plugin execution.

        Raises:
            PluginError: If there's an error executing the plugin.
        """
        return await asyncio.to_thread(self.execute_plugin, name, args)
