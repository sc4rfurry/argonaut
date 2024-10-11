from argonaut.plugins import Plugin, PluginMetadata, PluginContext
from typing import Dict, Any, List
import os
import re


class FileAnalyzerPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="file_analyzer",
            version="1.2.0",
            description="A plugin for analyzing files and performing text operations. (A practical example of how to create plugins for Argonaut)",
            author="sc4rfurry",
            website="https://github.com/sc4rfurry/Argonaut-Plugins",
            tags=["file", "analysis", "text"],
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
                                          |___/              
    """

    def initialize(self, context: PluginContext):
        self.context = context
        analyze_cmd = context.parser.add_subcommand("analyze", help="Analyze files")
        analyze_cmd.add("files", nargs="+", help="Files to analyze")
        analyze_cmd.add("--count", choices=["words", "lines", "chars"], help="Count words, lines, or characters")
        analyze_cmd.add("--search", help="Search for a specific term in the files")
        analyze_cmd.add("--replace", nargs=2, metavar=('SEARCH', 'REPLACE'), help="Replace SEARCH with REPLACE")
        analyze_cmd.add("--verbose", action="store_true", help="Enable verbose output")
        analyze_cmd.add("--quiet", action="store_true", help="Run in quiet mode (minimal output)")

        self.register_hook("before_analyze", self.before_analyze_callback)

    def execute(self, args: Dict[str, Any]) -> Any:
        if "files" not in args or not args["files"]:
            return "Error: No files specified for analysis."

        self.execute_hook("before_analyze", args)
        return self.analyze_files(args)

    def before_analyze_callback(self, args: Dict[str, Any]):
        self.log("Starting file analysis", "verbose")

    def analyze_files(self, args: Dict[str, Any]) -> str:
        results = []
        files = args.get("files", [])
        if isinstance(files, str):
            files = [files]

        for file_path in files:
            result = self.analyze_single_file(file_path, args)
            if result:
                results.append(result)

        return "\n".join(results)

    def analyze_single_file(self, file_path: str, args: Dict[str, Any]) -> str:
        if not file_path or file_path == ".":
            return f"Error: Invalid file path - {file_path}"

        if not os.path.exists(file_path):
            return f"Error: File not found - {file_path}"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            file_result = f"Analysis for {file_path}:\n"

            if args.get("count"):
                count_result = self.count_elements(content, args["count"])
                file_result += f"  {args['count'].capitalize()}: {count_result}\n"

            if args.get("search"):
                search_result = self.search_term(content, args["search"])
                file_result += f"  Occurrences of '{args['search']}': {search_result}\n"

            if args.get("replace"):
                if isinstance(args["replace"], list) and len(args["replace"]) == 2:
                    search_term, replace_term = args["replace"]
                    replaced_content, count = self.replace_term(content, search_term, replace_term)
                    file_result += f"  Replaced {count} occurrence(s) of '{search_term}' with '{replace_term}'\n"

                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(replaced_content)
                else:
                    file_result += "  Error: Invalid replace arguments\n"

            return file_result

        except PermissionError:
            return f"Error: Permission denied - {file_path}"
        except Exception as e:
            return f"Error processing {file_path}: {str(e)}"

    def count_elements(self, content: str, element: str) -> int:
        if element == "words":
            return len(content.split())
        elif element == "lines":
            return len(content.splitlines())
        elif element == "chars":
            return len(content)

    def search_term(self, content: str, term: str) -> int:
        return len(re.findall(re.escape(term), content, re.IGNORECASE))

    def replace_term(self, content: str, search: str, replace: str) -> tuple[str, int]:
        pattern = re.compile(re.escape(search), re.IGNORECASE)
        new_content, count = pattern.subn(replace, content)
        return new_content, count

    def cleanup(self):
        self.log("Cleaning up FileAnalyzerPlugin", "verbose")

    def log(self, message: str, level: str = "info"):
        if self.quiet:
            return
        if level == "verbose" and not self.verbose:
            return
        color_method = getattr(self.context.colored_output, level, self.context.colored_output.blue)
        self.context.logger.log(color_method(f"[{self.metadata.name}] {message}"), level.upper())