import importlib
import inspect
from typing import Any, Dict, List, Optional, Callable, Type
from abc import ABC, abstractmethod
import subprocess
import sys
from argonaut.fancy_output import ColoredOutput
from argonaut.logging import ArgonautLogger


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
    def __init__(self, parser, logger: ArgonautLogger, colored_output: ColoredOutput):
        self.parser = parser
        self.logger = logger
        self.colored_output = colored_output


class PluginHook:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.callbacks: List[Callable] = []

    def register(self, callback: Callable):
        self.callbacks.append(callback)

    def execute(self, *args, **kwargs):
        return [callback(*args, **kwargs) for callback in self.callbacks]


class Plugin(ABC):
    def __init__(self):
        self.context: Optional[PluginContext] = None
        self.verbose: bool = False
        self.quiet: bool = False
        self.hooks: Dict[str, PluginHook] = {}

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        pass

    @property
    def required_dependencies(self) -> List[str]:
        return ["argonaut"]

    @property
    def dependencies(self) -> List[str]:
        return []

    @property
    def banner(self) -> Optional[str]:
        return None

    @abstractmethod
    def initialize(self, context: PluginContext) -> None:
        pass

    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Any:
        pass

    def cleanup(self):
        pass

    def show_banner(self):
        if self.banner and not self.quiet:
            print(self.context.colored_output.blue(self.banner))

    def log(self, message: str, level: str = "info"):
        if self.quiet:
            return
        if level == "verbose" and not self.verbose:
            return
        color_method = getattr(
            self.context.colored_output, level, self.context.colored_output.blue
        )
        self.context.logger.log(
            color_method(f"[{self.metadata.name}] {message}"), level
        )

    def register_hook(self, hook_name: str, callback: Callable):
        if hook_name not in self.hooks:
            self.hooks[hook_name] = PluginHook(hook_name, f"Hook for {hook_name}")
        self.hooks[hook_name].register(callback)

    def execute_hook(self, hook_name: str, *args, **kwargs):
        if hook_name in self.hooks:
            return self.hooks[hook_name].execute(*args, **kwargs)
        return []


class PluginManager:
    def __init__(self, parser, logger: ArgonautLogger, colored_output: ColoredOutput):
        self.plugins: Dict[str, Plugin] = {}
        self.parser = parser
        self.logger = logger
        self.colored_output = colored_output
        self.hooks: Dict[str, PluginHook] = {}

    def load_plugin(self, module_path: str) -> None:
        try:
            module = importlib.import_module(module_path)
            plugin_class = self._find_plugin_class(module)
            if not plugin_class:
                raise PluginError(
                    module_path,
                    f"No valid plugin class found in module '{module_path}'",
                )

            plugin_instance = plugin_class()
            if not isinstance(plugin_instance, Plugin):
                raise PluginError(
                    module_path, f"Plugin does not inherit from the Plugin base class"
                )

            context = PluginContext(self.parser, self.logger, self.colored_output)
            plugin_instance.context = context
            plugin_instance.initialize(context)

            self._install_dependencies(plugin_instance)

            self.plugins[plugin_instance.metadata.name] = plugin_instance
            self.logger.info(
                f"Loaded plugin: {plugin_instance.metadata.name} v{plugin_instance.metadata.version}"
            )

            # Register plugin hooks
            for hook_name, hook in plugin_instance.hooks.items():
                if hook_name not in self.hooks:
                    self.hooks[hook_name] = hook
                else:
                    for callback in hook.callbacks:
                        self.hooks[hook_name].register(callback)

        except ImportError as e:
            raise PluginError(module_path, f"Could not load plugin: {str(e)}")
        except Exception as e:
            raise PluginError(module_path, f"Error loading plugin: {str(e)}")

    def _install_dependencies(self, plugin: Plugin):
        # Always install 'argonaut' as a required dependency
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
        self.plugins[name].cleanup()
        del self.plugins[name]
        self.logger.info(f"Unloaded plugin: {name}")

    def execute_plugin(self, name: str, args: Dict[str, Any]) -> Any:
        if name not in self.plugins:
            raise PluginError(name, f"Plugin '{name}' is not loaded")
        plugin = self.plugins[name]
        plugin.verbose = args.get("verbose", False)
        plugin.quiet = args.get("quiet", False)
        plugin.show_banner()
        return plugin.execute(args)

    def _find_plugin_class(self, module) -> Optional[Type[Plugin]]:
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
        ]

    def get_plugin(self, name: str) -> Plugin:
        if name not in self.plugins:
            raise PluginError(name, f"Plugin '{name}' is not loaded")
        return self.plugins[name]

    def reload_plugin(self, name: str) -> None:
        if name not in self.plugins:
            raise PluginError(f"Plugin '{name}' is not loaded")

        plugin = self.plugins[name]
        module = inspect.getmodule(plugin.__class__)
        if not module:
            raise PluginError(f"Cannot reload plugin '{name}': module not found")

        try:
            importlib.reload(module)
            new_plugin_class = self._find_plugin_class(module)
            if not new_plugin_class:
                raise PluginError(
                    f"No valid plugin class found after reloading module for '{name}'"
                )

            new_plugin_instance = new_plugin_class()
            new_plugin_instance.context = plugin.context
            new_plugin_instance.initialize(plugin.context)

            self.plugins[name] = new_plugin_instance
            self.logger.info(f"Reloaded plugin: {name}")
        except Exception as e:
            raise PluginError(f"Error reloading plugin '{name}': {str(e)}")

    def get_plugins_by_tag(self, tag: str) -> List[Plugin]:
        return [
            plugin for plugin in self.plugins.values() if tag in plugin.metadata.tags
        ]


class PluginError(Exception):
    pass
