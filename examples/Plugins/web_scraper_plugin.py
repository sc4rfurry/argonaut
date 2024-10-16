#/usr/bin/env python3
# -*- coding: utf-8 -*-
from argonaut.plugins import Plugin, PluginMetadata, PluginContext
from typing import Dict, Any, List
import asyncio
import aiohttp
from bs4 import BeautifulSoup


class WebScraperPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="web_scraper",
            version="1.0.0",
            description="An example plugin for scraping web pages.",
            author="sc4rfurry",
            website="https://github.com/sc4rfurry",
            tags=["web", "scraper", "async"],
        )

    @property
    def dependencies(self) -> List[str]:
        return ["aiohttp", "beautifulsoup4"]

    @property
    def banner(self) -> str:
        return r"""
     __          __  _     _____                                
     \ \        / / | |   / ____|                               
      \ \  /\  / /__| |__| (___   ___ _ __ __ _ _ __   ___ _ __ 
       \ \/  \/ / _ \ '_ \\___ \ / __| '__/ _` | '_ \ / _ \ '__|
        \  /\  /  __/ |_) |___) | (__| | | (_| | |_) |  __/ |   
         \/  \/ \___|_.__/_____/ \___|_|  \__,_| .__/ \___|_|   
                                               | |              
                                               |_|              
        """

    def initialize(self, context: PluginContext):
        self.context = context
        self.logger = context.logger
        scrape_cmd = context.parser.add_subcommand("scrape", help="Scrape a web page")
        scrape_cmd.add("--url", required=True, help="URL to scrape")
        scrape_cmd.add(
            "--async", action="store_true", help="Run the scraping asynchronously"
        )

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.run(self.scrape_url_async(args["url"]))

    async def execute_async(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return await self.scrape_url_async(args["url"])

    async def scrape_url_async(self, url: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    title = soup.title.string if soup.title else "No title found"
                    return {"url": url, "title": title, "status": response.status}
                else:
                    return {
                        "url": url,
                        "error": f"Failed to scrape. Status code: {response.status}",
                    }


def register_plugin():
    return WebScraperPlugin()
