# /usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os
from argonaut import Argonaut, ArgonautLogger, ColoredOutput, LogLevel, PluginContext
from argonaut.exceptions import ArgonautError, PluginError
from argonaut.plugins import PluginManager
from file_analyzer_plugin import FileAnalyzerPlugin


async def main():
    parser = Argonaut(description="File Analyzer Application")
    logger = ArgonautLogger.get_logger("FileAnalyzerApp", level=LogLevel.INFO)
    colored_output = ColoredOutput()

    # Add the global options
    parser.add_global_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_global_argument(
        "--quiet", "-q", action="store_true", help="Run in quiet mode (minimal output)"
    )
    parser.add_global_argument(
        "--debug", "-d", action="store_true", help="Enable debug mode"
    )

    # Set up the plugin manager
    plugin_manager = PluginManager(parser, logger, colored_output)

    # Create and initialize the FileAnalyzerPlugin
    file_analyzer = FileAnalyzerPlugin()
    context = PluginContext(parser, logger, colored_output)
    file_analyzer.initialize(context)
    plugin_manager.plugins["file_analyzer"] = file_analyzer

    try:
        # Parse arguments
        args = parser.parse()

        # Set up logging based on arguments
        if args.get("debug"):
            logger.set_level(LogLevel.DEBUG)
            print("Debug mode enabled.")
        elif args.get("verbose"):
            logger.set_level(LogLevel.INFO)
            print("Verbose mode enabled.")
        elif args.get("quiet"):
            logger.set_level(LogLevel.ERROR)

        if not args.get("quiet"):
            print(colored_output.green("Loaded plugins:"))
            for plugin in plugin_manager.list_plugins():
                print(
                    colored_output.yellow(
                        f"- {plugin['name']} v{plugin['version']} by {plugin['author']}"
                    )
                )
                print(colored_output.blue(f"  {plugin['description']}"))
                print(colored_output.blue(f"  Website: {plugin['website']}"))
                if plugin["tags"]:
                    print(colored_output.blue(f"  Tags: {', '.join(plugin['tags'])}"))

            print(colored_output.blue(file_analyzer.get_system_info()))
            print(colored_output.blue(file_analyzer.banner))

        # Execute the plugin if needed
        if args.get("subcommand") == "analyze":
            try:
                # Convert relative paths to absolute paths
                if args.get("files"):
                    args["files"] = [os.path.abspath(file) for file in args["files"]]
                if args.get("directory"):
                    args["directory"] = os.path.abspath(args["directory"])

                if args.get("async"):
                    result = await plugin_manager.execute_plugin_async(
                        "file_analyzer", args
                    )
                else:
                    result = plugin_manager.execute_plugin("file_analyzer", args)
                print(result)
            except PluginError as e:
                print(colored_output.red(f"Plugin error: {str(e)}"))
        else:
            parser.print_help()

    except ArgonautError as e:
        print(colored_output.red(f"Error: {str(e)}"))
    finally:
        print(colored_output.blue("Exiting..."))


if __name__ == "__main__":
    asyncio.run(main())
