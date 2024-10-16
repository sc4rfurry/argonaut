# /usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from argonaut import (
    Argonaut,
    PluginManager,
    ArgonautLogger,
    ColoredOutput,
    LogLevel,
    PluginContext,
)
from Plugins.web_scraper_plugin import WebScraperPlugin


async def main():
    parser = Argonaut(description="Web Scraper Plugin Example")
    parser.add("--url", "-u", required=True, help="URL to scrape")

    logger = ArgonautLogger.get_logger("WebScraperExample", level=LogLevel.INFO)
    colored_output = ColoredOutput()

    plugin_manager = PluginManager(parser, logger, colored_output)

    web_scraper = WebScraperPlugin()
    context = PluginContext(parser, logger, colored_output)
    web_scraper.initialize(context)
    plugin_manager.plugins["web_scraper"] = web_scraper

    args = parser.parse()

    try:
        result = await plugin_manager.execute_plugin_async("web_scraper", args)
        print("Web Scraper Result:")
        for key, value in result.items():
            if key == "first_5_links":
                print(f"{key}:")
                for link in value:
                    print(f"  - {link}")
            else:
                print(f"{key}: {value}")
    except Exception as e:
        print(f"Error executing Web Scraper plugin: {e}")


if __name__ == "__main__":
    asyncio.run(main())
