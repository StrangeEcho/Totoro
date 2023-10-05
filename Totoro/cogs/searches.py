from discord.ext import commands
from core import TotoroBot

import logging
import asyncio
import discord
import async_cse


class Searches(commands.Cog):
    """Google search related commands"""

    def __init__(self, bot: TotoroBot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    async def cog_load(self):
        self.async_cse = async_cse.Search(self.bot.config.get("async_cse_apikey"))
        self.logger.info(
            "Finished establishing async_cse Client. Ready to interact with api..."
        )

    async def cog_unload(self):
        await self.async_cse.close()
        self.logger.info("Terminated async_cse Search Client")

    @commands.command()
    async def search(self, ctx: commands.Context, *, query: str):
        """Query google with a specific search content and return back search results"""
        try:
            results: list[async_cse.Result] = await self.async_cse.search(query)
            await ctx.send(
                embed=discord.Embed(
                    title=query,
                    description="\n\n".join(
                        [
                            f"[{search.title}]({search.url})\n{search.description}"
                            for search in results[:5]
                        ]
                    ),
                    color=discord.Color.green(),
                )
            )
        except async_cse.NoResults:
            return await ctx.send(f"No results found with query: {query}")


async def setup(bot: TotoroBot):
    await bot.add_cog(Searches(bot))
