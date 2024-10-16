# /usr/bin/env python3
# -*- coding: utf-8 -*-
from argonaut.plugins import Plugin, PluginMetadata, PluginContext
from typing import Dict, Any, List
import os
import re
import asyncio
import platform
from pathlib import Path


class FileAnalyzerPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="file_analyzer",
            version="1.6.0",
            description="A cross-platform plugin for analyzing and modifying text files and folders.",
            author="sc4rfurry",
            website="https://github.com/sc4rfurry/Argonaut-Plugins",
            tags=[
                "file",
                "folder",
                "analysis",
                "text",
                "search",
                "replace",
                "cross-platform",
            ],
        )

    @property
    def dependencies(self) -> List[str]:
        return []

    @property
    def banner(self) -> str:
        return r"""
     ______ _ _        ___              _                    
    |  ____(_) |      / _ \            | |                   
    | |__   _| | ___ / /_\ \_ __   __ _| |_   _ _______ _ __ 
    |  __| | | |/ _ \|  _  | '_ \ / _` | | | | |_  / _ \ '__|
    | |    | | |  __/| | | | | | | (_| | | |_| |/ /  __/ |   
    |_|    |_|_|\___\\_| |_/_| |_|\__,_|_|\__, /___\___|_|   
                                           __/ |             
                                          |___/   A cross-platform file analysis plugin..!           
    """

    def initialize(self, context: PluginContext):
        self.context = context
        self.logger = context.logger
        self.verbose = False
        self.quiet = False
        analyze_cmd = context.parser.add_subcommand(
            "analyze", help="Analyze files and folders"
        )
        analyze_cmd.add("--files", "-f", nargs="+", help="Files to analyze")
        analyze_cmd.add("--directory", "-d", help="Directory to analyze")
        analyze_cmd.add(
            "--count",
            choices=["words", "lines", "chars"],
            help="Count words, lines, or characters",
        )
        analyze_cmd.add("--search", help="Search for a specific term (regex supported)")
        analyze_cmd.add(
            "--replace",
            nargs=2,
            metavar=("SEARCH", "REPLACE"),
            help="Replace text (regex supported)",
        )
        analyze_cmd.add(
            "--recursive", "-r", action="store_true", help="Analyze folders recursively"
        )
        analyze_cmd.add(
            "--async", action="store_true", help="Run the analysis asynchronously"
        )
        analyze_cmd.add("--verbose", action="store_true", help="Enable verbose output")
        analyze_cmd.add(
            "--quiet", action="store_true", help="Run in quiet mode (minimal output)"
        )
        analyze_cmd.add(
            "--file-type", help="Filter files by extension (e.g., .txt, .py)"
        )
        analyze_cmd.add(
            "--size-limit",
            type=int,
            help="Limit analysis to files smaller than SIZE in bytes",
        )

        self.register_hook("before_analyze", self.before_analyze_callback)
        self.show_banner()

    def execute(self, args: Dict[str, Any]) -> Any:
        self.verbose = args.get("verbose", False)
        self.quiet = args.get("quiet", False)
        if not args.get("files") and not args.get("directory"):
            return "Error: No files or directory specified for analysis."

        self.execute_hook("before_analyze", args)
        return self.analyze_targets(args)

    async def execute_async(self, args: Dict[str, Any]) -> Any:
        self.logger.info("Executing File Analyzer plugin asynchronously")
        return await self.analyze_targets_async(args)

    def before_analyze_callback(self, args: Dict[str, Any]):
        self.log("Starting file/folder analysis", "verbose")

    def analyze_targets(self, args: Dict[str, Any]) -> str:
        results = []
        if args.get("files"):
            for file_path in args["files"]:
                path = Path(file_path).resolve()
                if path.is_file():
                    results.append(self.process_file(path, args))
                else:
                    results.append(f"Error: Invalid file path - {path}")

        if args.get("directory"):
            dir_path = Path(args["directory"]).resolve()
            if dir_path.is_dir():
                results.extend(self.process_directory(dir_path, args))
            else:
                results.append(f"Error: Invalid directory path - {dir_path}")

        return "\n\n".join(filter(None, results))

    async def analyze_targets_async(self, args: Dict[str, Any]) -> str:
        tasks = []
        if args.get("files"):
            for file_path in args["files"]:
                path = Path(file_path).resolve()
                if path.is_file():
                    tasks.append(self.process_file_async(path, args))
                else:
                    tasks.append(
                        asyncio.to_thread(lambda: f"Error: Invalid file path - {path}")
                    )

        if args.get("directory"):
            dir_path = Path(args["directory"]).resolve()
            if dir_path.is_dir():
                tasks.append(self.process_directory_async(dir_path, args))
            else:
                tasks.append(
                    asyncio.to_thread(
                        lambda: f"Error: Invalid directory path - {dir_path}"
                    )
                )

        results = await asyncio.gather(*tasks)
        # Flatten the results list and join into a single string
        flattened_results = []
        for result in results:
            if isinstance(result, list):
                flattened_results.extend(result)
            else:
                flattened_results.append(result)
        return "\n\n".join(filter(None, flattened_results))

    def process_file(self, file_path: Path, args: Dict[str, Any]) -> str:
        if not self._should_analyze_file(file_path, args):
            return None

        try:
            with file_path.open("r", encoding="utf-8") as file:
                content = file.read()

            result = f"Analysis for {file_path}:\n"
            result += f"  File size: {file_path.stat().st_size} bytes\n"
            result += f"  Last modified: {file_path.stat().st_mtime}\n"

            if args.get("count"):
                result += self.count_elements(content, args["count"])
            elif args.get("search"):
                result += self.search_content(content, args["search"])
            elif args.get("replace"):
                result += self.replace_content(file_path, content, args["replace"])
            else:
                result += self.default_analysis(content)

            return result
        except Exception as e:
            return f"Error processing {file_path}: {str(e)}"
        except Exception as e:
            return f"Error processing {file_path}: {str(e)}"

    def process_directory(self, dir_path: Path, args: Dict[str, Any]) -> List[str]:
        results = []
        if args.get("recursive"):
            for root, _, files in os.walk(dir_path):
                for file in files:
                    file_path = Path(root) / file
                    if self._should_analyze_file(file_path, args):
                        results.append(self.process_file(file_path, args))
        else:
            results.append(f"Contents of {dir_path}:")
            for item in dir_path.iterdir():
                if item.is_file() and self._should_analyze_file(item, args):
                    results.append(f"  {item.name}")
        return list(filter(None, results))

    async def process_file_async(self, file_path: Path, args: Dict[str, Any]) -> str:
        return await asyncio.to_thread(self.process_file, file_path, args)

    async def process_directory_async(
        self, dir_path: Path, args: Dict[str, Any]
    ) -> List[str]:
        results = await asyncio.to_thread(self.process_directory, dir_path, args)
        return [result for result in results if isinstance(result, str)]

    def count_elements(self, content: str, element: str) -> str:
        if element == "words":
            count = len(content.split())
            return f"  Word count: {count}"
        elif element == "lines":
            count = len(content.splitlines())
            return f"  Line count: {count}"
        elif element == "chars":
            count = len(content)
            return f"  Character count: {count}"

    def search_content(self, content: str, term: str) -> str:
        matches = list(re.finditer(term, content, re.MULTILINE))
        if matches:
            results = [
                f"  Line {content.count(chr(10), 0, m.start()) + 1}: {m.group()}"
                for m in matches
            ]
            return f"Occurrences of '{term}':\n" + "\n".join(results)
        return f"No matches found for '{term}'"

    def replace_content(
        self, file_path: Path, content: str, replace_args: List[str]
    ) -> str:
        search, replace = replace_args
        new_content, count = re.subn(search, replace, content, flags=re.MULTILINE)
        if count > 0:
            with file_path.open("w", encoding="utf-8") as file:
                file.write(new_content)
            return f"Replaced {count} occurrence(s) of '{search}' with '{replace}'"
        return f"No replacements made for '{search}'"

    def default_analysis(self, content: str) -> str:
        words = len(content.split())
        lines = len(content.splitlines())
        chars = len(content)
        return f"  Words: {words}\n  Lines: {lines}\n  Characters: {chars}"

    def cleanup(self):
        self.log("Cleaning up FileAnalyzerPlugin", "verbose")

    def log(self, message: str, level: str = "info"):
        if self.quiet:
            return
        if level == "verbose" and not self.verbose:
            return
        color_method = getattr(
            self.context.colored_output, level, self.context.colored_output.blue
        )
        self.context.logger.log(
            color_method(f"[{self.metadata.name}] {message}"), level.upper()
        )

    def _should_analyze_file(self, file_path: Path, args: Dict[str, Any]) -> bool:
        if args.get("file_type") and not str(file_path).lower().endswith(
            args["file_type"].lower()
        ):
            return False
        if args.get("size_limit") and file_path.stat().st_size > args["size_limit"]:
            return False
        return True

    def get_system_info(self) -> str:
        return f"Running on {platform.system()} {platform.release()} ({platform.machine()})"
