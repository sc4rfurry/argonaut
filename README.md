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
4. [Quick Start](#-quick-start)
5. [Advanced Usage](#-advanced-usage)
6. [Plugin System](#-plugin-system)
7. [API Reference](#-api-reference)
8. [Examples](#-examples)
9. [Contributing](#-contributing)
10. [License](#-license)

---

## 🚀 Introduction

**ArgøNaut** is a sophisticated and flexible command-line argument parsing library for Python applications. It extends the capabilities of standard argument parsing libraries with advanced features, a robust plugin system, and cross-platform compatibility.

---

## ✨ Features

- 🎨 Intuitive API for defining and parsing arguments
- 🌳 Support for subcommands and nested command structures
- 🔌 Robust plugin system for extensibility
- 💻 Cross-platform compatibility (Windows, macOS, Linux)
- 🛡️ Advanced input sanitization and error handling
- 📚 Customizable help generation and formatting
- 🐚 Shell completion script generation for multiple shells
- 📊 Progress bar and colored output capabilities
- 📁 Configuration file support (YAML, JSON)
- 🌿 Environment variable integration
- 📘 Automatic man page generation
- ⚡ Asynchronous support for argument parsing and plugin execution

---

## 📦 Installation

Install ArgøNaut using pip:
```bash
pip install argonautCli
```

## 🚀 Quick Start

```python
from argonaut import Argonaut


parser = Argonaut(description="My awesome CLI tool")
parser.add("--name", help="Your name")
parser.add("--age", type=int, help="Your age")
args = parser.parse()

print(f"Hello, {args['name']}! You are {args['age']} years old.")
```

## 🔧 Advanced Usage

### Asynchronous Support

```python
import asyncio
from argonaut import Argonaut


parser = Argonaut()
parser.add("--async-option", help="An async option")

async def main():
   args = await parser.parse_async()
   result = await parser.execute_plugin_async("my_plugin", args)
   
print(result)
```

### Environment Variables

```python
from argonaut import Argonaut


parser = Argonaut()
parser.add("--api-key", env_var="API_KEY", help="API key (can be set via API_KEY env var)")
args = parser.parse()

print(f"API Key: {args['api_key']}")
```

## 🔌 Plugin System

ArgøNaut features a powerful plugin system that allows you to extend the functionality of your CLI applications.

```python
from argonaut import Plugin, PluginMetadata
import asyncio


class MyPlugin(Plugin):
   @property
   def metadata(self) -> PluginMetadata:
      return PluginMetadata(
      name="my_plugin",
      version="1.0.0",
      description="A sample plugin for ArgøNaut",
      author="Your Name",
      website="https://example.com",
      tags=["sample", "demo"]
      )

   def initialize(self, context):
      self.context = context
   def execute(self, args):
      return f"Hello from MyPlugin! Args: {args}"
   async def execute_async(self, args):
      # Asynchronous execution method
      return await some_async_operation(args)

def on_load(self):
print("Plugin loaded")

def on_unload(self):
print("Plugin unloaded")

def on_command_execution(self, command):
print(f"Command '{command}' is being executed")
```


---

## 📚 API Reference

For a complete API reference, please visit our [documentation](https://sc4rfurry.github.io/Argonaut-Docs/).

---

## 📋 Examples

For more examples, please refer to the [examples](examples/) directory in the repository.

---

## 🤝 Contributing

We welcome contributions to ArgøNaut! Please see our [Contributing Guide](CONTRIBUTING.md) for more details on how to get started.

---

## 📄 License

ArgøNaut is released under the MIT License. See the [LICENSE](LICENSE) file for full details.

---

For more information and detailed documentation, visit [ArgøNaut's Documentation](https://sc4rfurry.github.io/Argonaut-Docs/).