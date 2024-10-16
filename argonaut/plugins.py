# /usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import inspect
from typing import Any, Dict, List, Optional, Callable, Type, Union
from abc import ABC, abstractmethod
import subprocess
import sys
from argonaut.fancy_output import ColoredOutput
from argonaut.logging import ArgonautLogger
import yaml
import json
from pathlib import Path
import asyncio
from argonaut.exceptions import PluginError, PluginLoadError, PluginExecutionError


class PluginMetadata:
    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        author: str,
        website: str,
        tags: List[str] = None,
    ):
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.website = website
        self.tags = tags or []


class PluginContext:
    def __init__(
        self, parser: Any, logger: ArgonautLogger, colored_output: ColoredOutput
    ):
        self.parser = parser
        self.logger = logger
        self.colored_output = colored_output


class PluginHook:
    def __init__(self):
        self.callbacks: List[Callable] = []

    def register(self, callback: Callable):
        self.callbacks.append(callback)

    def unregister(self, callback: Callable):
        self.callbacks.remove(callback)

    def execute(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)


class Plugin(ABC):
    def __init__(self):
        self.context: Optional[PluginContext] = None
        self.verbose: bool = False
        self.quiet: bool = False
        self.hooks: Dict[str, PluginHook] = {}
        self.config: Dict[str, Any] = {}

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        pass

    @property
    def required_dependencies(self) -> List[str]:
        return ["argonautCli"]

    @property
    def dependencies(self) -> List[str]:
        return []

    @property
    def banner(self) -> Optional[str]:
        return None

    @property
    def plugin_dependencies(self) -> List[str]:
        return []

    @abstractmethod
    def initialize(self, context: PluginContext) -> None:
        self.context = context
        self.logger = context.logger
        self.logger.info(f"Initializing plugin: {self.metadata.name}")
        # Load configuration if available
        config_path = Path(f"{self.metadata.name.lower()}_config.yaml")
        if config_path.exists():
            self.load_config(config_path)

    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Any:
        self.logger.info(f"Executing plugin: {self.metadata.name}")
        raise NotImplementedError("Plugin execution not implemented")

    @abstractmethod
    async def execute_async(self, args: Dict[str, Any]) -> Any:
        self.logger.info(f"Executing plugin asynchronously: {self.metadata.name}")
        raise NotImplementedError("Asynchronous plugin execution not implemented")

    def cleanup(self) -> None:
        self.logger.info(f"Cleaning up plugin: {self.metadata.name}")

    def show_banner(self):
        if self.banner and not self.quiet:
            self.context.colored_output.print(self.banner, color="blue")

    def log(self, message: str, level: str = "info"):
        if self.quiet:
            return
        if level == "verbose" and not self.verbose:
            return
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(f"[{self.metadata.name}] {message}")

    def register_hook(self, hook_name: str, callback: Callable):
        if hook_name not in self.hooks:
            self.hooks[hook_name] = PluginHook()
        self.hooks[hook_name].register(callback)

    def execute_hook(self, hook_name: str, *args, **kwargs):
        if hook_name in self.hooks:
            return self.hooks[hook_name].execute(*args, **kwargs)
        return []

    def load_config(self, config_file: Union[str, Path]):
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with config_path.open() as f:
            if config_path.suffix in (".yaml", ".yml"):
                self.config = yaml.safe_load(f)
            elif config_path.suffix == ".json":
                self.config = json.load(f)
            else:
                raise ValueError(
                    f"Unsupported config file format: {config_path.suffix}"
                )

    def on_load(self) -> None:
        self.logger.info(f"Plugin loaded: {self.metadata.name}")

    def on_unload(self) -> None:
        self.logger.info(f"Plugin unloaded: {self.metadata.name}")

    def on_command_execution(self, command: str) -> None:
        self.logger.info(
            f"Executing command '{command}' in plugin: {self.metadata.name}"
        )

    async def on_command_execution_async(self, command: str):
        await asyncio.to_thread(self.on_command_execution, command)

    def get_config_value(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set_config_value(self, key: str, value: Any):
        self.config[key] = value

    def save_config(self):
        config_path = Path(f"{self.metadata.name.lower()}_config.yaml")
        with config_path.open("w") as f:
            yaml.dump(self.config, f)


class PluginManager:
    def __init__(self, parser, logger: ArgonautLogger, colored_output: ColoredOutput):
        self.plugins: Dict[str, Union[Plugin, str]] = {}
        self.parser = parser
        self.logger = logger
        self.colored_output = colored_output
        self.hooks: Dict[str, PluginHook] = {}

    def load_plugin(self, module_path: str) -> None:
        try:
            spec = importlib.util.spec_from_file_location("plugin_module", module_path)
            if spec is None:
                raise PluginLoadError(
                    module_path, f"Could not find module: {module_path}"
                )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                raise PluginLoadError(
                    module_path,
                    f"No valid plugin class found in module '{module_path}'",
                )

            plugin_instance = plugin_class()
            if not isinstance(plugin_instance, Plugin):
                raise PluginLoadError(
                    module_path,
                    f"Plugin class does not inherit from the Plugin base class",
                )

            context = PluginContext(self.parser, self.logger, self.colored_output)
            plugin_instance.initialize(context)

            self._install_dependencies(plugin_instance)

            self.plugins[plugin_instance.metadata.name] = plugin_instance
            self.logger.info(
                f"Loaded plugin: {plugin_instance.metadata.name} v{plugin_instance.metadata.version}"
            )

            plugin_instance.on_load()

        except Exception as e:
            raise PluginLoadError(module_path, f"Error loading plugin: {str(e)}")

    def _install_dependencies(self, plugin: Plugin):
        required_deps = plugin.required_dependencies + plugin.dependencies
        if required_deps:
            self.logger.info(
                f"Installing dependencies for plugin: {plugin.metadata.name}"
            )
            for dep in required_deps:
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                except subprocess.CalledProcessError:
                    raise PluginError(
                        plugin.metadata.name, f"Failed to install dependency: {dep}"
                    )

    def unload_plugin(self, name: str) -> None:
        if name not in self.plugins:
            raise PluginError(f"Plugin '{name}' is not loaded")
        plugin = self.plugins[name]
        plugin.on_unload()
        plugin.cleanup()
        del self.plugins[name]
        self.logger.info(f"Unloaded plugin: {name}")

    def execute_plugin(self, name: str, args: Dict[str, Any]) -> Any:
        if name not in self.plugins:
            raise PluginError(name, f"Plugin '{name}' not found")
        plugin = self.plugins[name]
        try:
            plugin.on_command_execution(name)
            return plugin.execute(args)
        except Exception as e:
            raise PluginExecutionError(name, f"Error executing plugin: {str(e)}")

    async def execute_plugin_async(self, name: str, args: Dict[str, Any]) -> Any:
        if name not in self.plugins:
            raise PluginError(name, f"Plugin '{name}' not found")
        plugin = self.plugins[name]
        try:
            await plugin.on_command_execution_async(name)
            if hasattr(plugin, "execute_async") and asyncio.iscoroutinefunction(
                plugin.execute_async
            ):
                return await plugin.execute_async(args)
            else:
                self.logger.warning(
                    f"Plugin '{name}' does not have an async execute method. Falling back to sync execution."
                )
                return await asyncio.to_thread(plugin.execute, args)
        except Exception as e:
            raise PluginExecutionError(
                name, f"Error executing plugin asynchronously: {str(e)}"
            )

    def _find_plugin_class(self, module) -> Type[Plugin]:
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Plugin) and obj is not Plugin:
                return obj
        return None

    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": plugin.metadata.name,
                "version": plugin.metadata.version,
                "description": plugin.metadata.description,
                "author": plugin.metadata.author,
                "website": plugin.metadata.website,
                "tags": plugin.metadata.tags,
            }
            for plugin in self.plugins.values()
            if isinstance(plugin, Plugin)
        ]

    def get_plugins_by_tag(self, tag: str) -> List[Plugin]:
        return [
            plugin
            for plugin in self.plugins.values()
            if isinstance(plugin, Plugin) and tag in plugin.metadata.tags
        ]
