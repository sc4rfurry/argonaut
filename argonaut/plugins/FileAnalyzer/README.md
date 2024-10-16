# File Analyzer Plugin for ArgøNaut

## 📚 Table of Contents

1. [Introduction](#-introduction)
2. [Features](#-features)
3. [Installation](#-installation)
4. [Usage](#-usage)
5. [Plugin Structure](#-plugin-structure)
6. [Example Implementation](#-example-implementation)
7. [Contributing](#-contributing)

## 🚀 Introduction

The File Analyzer Plugin is a powerful extension for the **ArgøNaut** argument parsing library. It provides functionality to analyze files and directories, perform text operations, and generate insightful reports.

## ✨ Features

- 📊 Count words, lines, or characters in file(s)
- 🔍 Search for specific terms within file(s) (supports regex)
- 🔄 Replace text in file(s) (supports regex)
- 📁 Analyze single file, multiple files or entire directories
- 🔁 Recursive directory analysis
- 📝 Detailed analysis reports
- 🎨 Customizable output formatting
- ⚡ Asynchronous processing support
- 🔢 File size limit filtering
- 📎 File type filtering

## 📦 Installation

1. Ensure ArgøNaut is installed:   
```bash
   pip install argonautCli   
```

2. Place `file_analyzer_plugin.py` in your project's plugin directory.

## 🛠 Usage

The File Analyzer Plugin adds the `analyze` subcommand to your ArgøNaut-based CLI application. Here's how to use it:

```bash
python usage.py analyze [OPTIONS] (--files FILE... | --directory DIR)
```


### Options:

- `--files FILE...`, `-f FILE...`: Specify one or more files to analyze
- `--directory DIR`, `-d DIR`: Specify a directory to analyze
- `--count {words,lines,chars}`: Count words, lines, or characters in files
- `--search TERM`: Search for a specific term in the files (regex supported)
- `--replace SEARCH REPLACE`: Replace text in files (regex supported)
- `--recursive`, `-r`: Analyze folders recursively
- `--async`: Run the analysis asynchronously
- `--verbose`: Enable verbose output
- `--quiet`: Run in quiet mode (minimal output)
- `--file-type EXT`: Filter files by extension (e.g., .txt, .py)
- `--size-limit BYTES`: Limit analysis to files smaller than SIZE in bytes

## 🧱 Plugin Structure

The plugin is defined in `file_analyzer_plugin.py` and consists of:

1. `FileAnalyzerPlugin` class (inherits from `Plugin`)
2. Metadata definition
3. Initialization method to set up CLI arguments
4. Execution methods for synchronous and asynchronous processing
5. File and directory analysis methods
6. Utility methods for counting, searching, and replacing text

## 📘 Example Implementation

See the `usage.py` file for an example of how to integrate and use the File Analyzer Plugin in your ArgøNaut application.

Now, here are the full CLI commands for usage.py:
1. Analyze a single file:
```bash
python usage.py analyze --files file.txt
```

2. Analyze multiple files:
```bash
python usage.py analyze --files file1.txt file2.txt file3.txt
```

3. Analyze a directory (non-recursive):
```bash
python usage.py analyze --directory /path/to/directory
```

4. Analyze a directory recursively:
```bash
python usage.py analyze --directory /path/to/directory --recursive
```

5. Count words in files:
```bash
python usage.py analyze --files file.txt --count words
```

6. Count lines in files:
```bash
python usage.py analyze --files file.txt --count lines
```

7. Count characters in files:
```bash
python usage.py analyze --files file.txt --count chars
```

8. Search for a term in files:
```bash
python usage.py analyze --files file.txt --search "pattern"
```

9. Replace text in files:
```bash
python usage.py analyze --files file.txt --replace "old_text" "new_text"
```

10. Analyze files with a specific extension:
```bash
python usage.py analyze --directory /path/to/directory --file-type .py
```

11. Analyze files smaller than a specific size:
```bash
python usage.py analyze --directory /path/to/directory --size-limit 1000000
```

12. Run analysis asynchronously:
```bash
python usage.py analyze --files file.txt --async
```

13. Enable verbose output:
```bash
python usage.py analyze --files file.txt --verbose
```

14.Run in quiet mode:
```bash
python usage.py analyze --files file.txt --quiet
```

15. Combine multiple options:
```bash
python usage.py analyze --directory /path/to/directory --recursive --file-type .txt --count words --verbose --async
```

16. Show help information:
```bash
python usage.py --help
```

17. Show help information for the analyze subcommand:
```bash
python usage.py analyze --help
```

##

## 🤝 Contributing

Contributions to ArgøNaut and its plugins are welcome! Please submit pull requests or open issues on the project repository.

---

## 📄 License

ArgøNaut is released under the MIT License. See the [LICENSE](LICENSE) file for full details.

---