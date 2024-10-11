# ArgøNaut: Advanced Argument Parsing Library

<p align="center">
  <img src="Docs/Argonaut-Logo.png" alt="ArgøNaut Logo" width="60%" style="max-width: 500px;">
</p>

<p align="center">
  <a href="https://github.com/sc4rfurry/argonaut"><img src="https://img.shields.io/github/stars/sc4rfurry/Argonaut?style=social" alt="GitHub stars"></a>
  <a href="https://github.com/sc4rfurry/argonaut/issues"><img src="https://img.shields.io/github/issues/sc4rfurry/Argonaut" alt="GitHub issues"></a>
  <a href="https://github.com/sc4rfurry/argonaut/blob/main/LICENSE"><img src="https://img.shields.io/github/license/sc4rfurry/Argonaut" alt="License"></a>
</p>

---

## 📚 Table of Contents

1. [Introduction](#introduction)
2. [Features](#-features)
3. [Installation](#-installation)
4. [Project Structure](#-project-structure)
5. [Core Components](#-core-components)
6. [Plugin System](#-plugin-system)
    - [Example Plugins](#-example-plugin)
7. [Utility Modules](#-utility-modules)
8. [Usage Examples](#-usage-examples)
    - [Examples](#examples)
9. [Contributing](#-contributing)
10. [License](#-license)

---

## 🚀 Introduction

**ArgøNaut** is a sophisticated argument parsing library for Python, designed to provide developers with a powerful, flexible, and user-friendly tool for building command-line interfaces (CLIs). It extends the capabilities of the standard `argparse` library with advanced features and a robust plugin system.

---

## ✨ Features

- 🎨 Intuitive API similar to argparse
- 🌳 Support for subcommands
- 🔧 Custom argument types and validators
- 🌿 Environment variable integration
- 💻 Interactive mode
- 🔌 Extensible plugin system
- 📊 Progress bar and fancy output options
- 🔒 Secure input handling
- 🔀 Mutually exclusive arguments
- 📁 Argument groups

---

## 📦 Installation

Install ArgøNaut using pip:

```bash
pip install argonaut
```

---

## 📁 Project Structure

```bash
Argonaut/
├── argonaut/
│   ├── __init__.py
│   ├── arguments.py
│   ├── core.py
│   ├── decorators.py
│   ├── exceptions.py
│   ├── fancy_output.py
│   ├── input_sanitizer.py
│   ├── logging.py
│   ├── plugins.py
│   ├── shell_completion.py
│   ├── utils.py
│   └── plugins/
│       └── FileAnalyzer/
│           ├── __init__.py
│           ├── file_analyzer_plugin.py
│           ├── README.md
│           └── usage.py
├── Docs/
│   ├── Argonaut-Logo.png
│   ├── index.html
│   ├── script.js
│   └── style.css
├── examples/
│   └── (Examples with usage of Argonaut)
├── LICENSE
├── setup.py
├── requirements.txt
└── README.md
```

---

## 🧱 Core Components

### 1. core.py
The heart of ArgøNaut, containing the main `Argonaut` class that handles argument parsing, subcommands, and plugin management.

### 2. arguments.py
Defines the `Argument`, `ArgumentGroup`, and `MutuallyExclusiveGroup` classes for creating and managing CLI arguments.

### 3. decorators.py
Provides decorators for enhancing argument functionality, such as `env_var`, `dynamic_default`, and `custom_validator`.

### 4. exceptions.py
Custom exception classes for ArgøNaut-specific errors.

---

## 🔌 Plugin System

The plugin system in ArgøNaut is implemented in `plugins.py`, allowing for easy extension of ArgøNaut's functionality. Key components include:

- `Plugin`: Base class for creating plugins
- `PluginManager`: Handles loading, unloading, and executing plugins
- `PluginMetadata`: Stores metadata about plugins

### Deep Dive into the Plugin System

The plugin system is designed to be flexible and easy to use, enabling developers to extend ArgøNaut's capabilities without modifying the core library. Plugins can add new commands, modify existing behavior, or integrate with external systems.

#### Key Components

1. **Plugin Base Class**: 
   - Provides a standard interface for all plugins.
   - Defines lifecycle methods like `initialize`, `execute`, and `cleanup`.

2. **PluginManager**:
   - Manages the lifecycle of plugins.
   - Responsible for loading plugins from specified directories and executing them.

3. **PluginMetadata**:
   - Stores information about each plugin, such as name, version, and author.

### Detailed Description of the Plugin Class

The `Plugin` class is an abstract base class that all plugins must inherit from. It provides a structured way to define plugins with the following key methods and properties:

- **Properties**:
  - `metadata`: Abstract property that must return a `PluginMetadata` object containing the plugin's metadata.
  - `required_dependencies`: List of dependencies that are required for the plugin to function.
  - `dependencies`: List of optional dependencies.
  - `banner`: Optional string to display when the plugin is loaded.

- **Methods**:
  - `initialize(context: PluginContext)`: Abstract method to initialize the plugin with the given context.
  - `execute(args: Dict[str, Any])`: Abstract method to execute the plugin's main functionality.
  - `cleanup()`: Method to perform any necessary cleanup when the plugin is unloaded.
  - `show_banner()`: Displays the plugin's banner if available.
  - `log(message: str, level: str = "info")`: Logs a message using the plugin's logger.
  - `register_hook(hook_name: str, callback: Callable)`: Registers a callback for a specific hook.
  - `execute_hook(hook_name: str, *args, **kwargs)`: Executes all callbacks registered to a specific hook.

### SOP for Creating Custom Plugins

To create a custom plugin, follow these steps:

1. **Create a New Plugin Directory**:
   - Inside the `plugins/` directory, create a new folder for your plugin, e.g., `MyCustomPlugin/`.

2. **Define the Plugin Class**:
   - Create a new Python file, e.g., `my_custom_plugin.py`.
   - Import the `Plugin` base class and define your plugin class.

3. **Implement Required Methods**:
   - Implement the `initialize`, `execute`, and `cleanup` methods to define your plugin's behavior.

4. **Add Metadata**:
   - Define a `PluginMetadata` object with details about your plugin.

5. **Test Your Plugin**:
   - Ensure your plugin works as expected by integrating it with an ArgøNaut application.

### Practical Example: File Analyzer Plugin

Below is a simplified example of how the `file_analyzer_plugin.py` might be structured:

````python
from argonaut.plugins import Plugin, PluginMetadata

class FileAnalyzerPlugin(Plugin):
    metadata = PluginMetadata(
        name="File Analyzer",
        version="1.0",
        author="Your Name",
        description="Analyzes files and provides insights."
    )

    def initialize(self, context):
        # Initialization logic here
        self.context = context

    def execute(self, args):
        # Main logic for analyzing files
        print(f"Analyzing file: {args['file_path']}")
        # ... additional logic ...

    def cleanup(self):
        # Cleanup logic here
        pass
````

This example demonstrates a basic plugin structure. Customize the `execute` method to perform specific tasks, such as reading a file, processing data, or generating reports.

For more detailed examples and advanced usage, refer to the documentation and example scripts.

### 🧩 Example Plugin

There is one Custom Plugin already implemented: `FileAnalyzerPlugin`.
For more information about this plugin, please refer to the [README](argonaut/plugins/FileAnalyzer/README.md) in the plugin's directory.

---

## 🛠 Utility Modules

### 1. fancy_output.py
Provides the `ColoredOutput` class for styled console output and `ProgressBar` for displaying progress.

### 2. input_sanitizer.py
Contains the `sanitize_input` function for secure input handling.

### 3. logging.py
Implements `ArgonautLogger` for customized logging functionality.

### 4. shell_completion.py
Generates shell completion scripts for Bash, Zsh, and Fish.

### 5. utils.py
Utility functions like `get_input_with_autocomplete` for enhanced user interaction.

---

## 🚀 Usage Examples

Basic usage:

```python
from argonaut import Argonaut

parser = Argonaut(description="My CLI App")
parser.add("--name", help="Your name")
parser.add("--age", type=int, help="Your age")
args = parser.parse()

print(f"Hello, {args['name']}! You are {args['age']} years old.")
```

For more advanced usage, including plugins and subcommands, refer to the documentation or visit [Argonaut's Documentation](https://sc4rfurry.github.io/Argonaut-Docs/).

### Examples

For more examples, please refer to the [examples](examples/) directory.

```bash
Argonaut/
├── argonaut/
│   ├── __init__.py
│   ├── arguments.py
│   ├── core.py
│   ├── decorators.py
│   ├── exceptions.py
│   ├── fancy_output.py
│   ├── input_sanitizer.py
│   ├── logging.py
│   ├── plugins.py
│   ├── shell_completion.py
│   ├── utils.py
│   └── plugins/
│       └── FileAnalyzer/
│           ├── (--- File Analyzer Plugin ---)
├── Docs/
│   ├── (Documentation for Argonaut and its Plugins)
├── examples/
    └── (Examples with usage of Argonaut)
```

---

## 🤝 Contributing

Contributions to ArgøNaut are welcome!

---

## 📄 License

ArgøNaut is released under the MIT License. See the [LICENSE](LICENSE) file for full details.

---
