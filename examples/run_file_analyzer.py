# /usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from argonaut import Argonaut, ArgonautLogger, ColoredOutput, LogLevel, PluginContext
from argonaut.exceptions import ArgonautError, PluginError
from argonaut.plugins import PluginManager
from Plugins.file_analyzer_plugin import FileAnalyzerPlugin


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
        args = parser.parse()

        if args.get("debug"):
            logger.set_level(LogLevel.DEBUG)
        elif args.get("verbose"):
            logger.set_level(LogLevel.INFO)
        elif args.get("quiet"):
            logger.set_level(LogLevel.ERROR)

        if args.get("subcommand") == "analyze":
            if args.get("async"):
                result = await plugin_manager.execute_plugin_async(
                    "file_analyzer", args
                )
            else:
                result = plugin_manager.execute_plugin("file_analyzer", args)
            print(result)
        else:
            parser.print_help()

    except ArgonautError as e:
        print(f"Error: {str(e)}")
    except PluginError as e:
        print(f"Plugin error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
