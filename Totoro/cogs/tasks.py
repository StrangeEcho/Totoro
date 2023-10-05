from core import TotoroBot
from discord.ext import commands, tasks
from itertools import cycle

import logging
import discord
import asyncio


class Tasks(commands.Cog):
    def __init__(self, bot: TotoroBot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.lavalink_setup.start()
        self.activity_cycler.start()

    @tasks.loop()
    async def lavalink_setup(self):
        await self.bot.wait_until_ready()
        if self.bot.node_pool.node_count == 0:
            await self.bot.node_pool.create_node(
                bot=self.bot,
                host="127.0.0.1",
                port=2333,
                password="youshallnotpass",
                identifier="totoro-local",
                spotify_client_id=self.bot.config.get("spotify_client_id", category="lavalink"),
                spotify_client_secret=self.bot.config.get(
                    "spotify_client_secret", category="lavalink"
                )
            )
    
    @tasks.loop()
    async def activity_cycler(self):
        activities = [
            discord.Game("with your feelings"),
            discord.Activity(
                type=discord.ActivityType.listening,
                name="to music with your mom"
            ),
            discord.Game(f"with {len(self.bot.users)} users")
        ]
        await self.bot.wait_until_ready()
        for act in cycle(activities):
            await self.bot.change_presence(activity=act)
            self.logger.info(f"Changed bot activity to: {act}")
            await asyncio.sleep(360)

        
async def setup(bot: TotoroBot):
    await bot.add_cog(Tasks(bot))
