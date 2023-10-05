from discord.ext import commands
from typing import Any, Optional
from datetime import datetime

import traceback
import os
import tomllib
import logging
import discord
import pomice


class TotoroConfigHandler:
    """A simple config helper for Totoro"""

    with open("./Totoro/core/config.toml", "rb") as confile:
        config: dict[Any, Any] = tomllib.load(confile)

    def get(self, config_name: str, *, category: Optional[str] = None) -> Optional[Any]:
        """Fetch the specified config from the config.toml file"""
        if category:
            try:
                return self.config[category][config_name]
            except KeyError:
                return None
        return self.config.get(config_name)


class TotoroBot(commands.AutoShardedBot):
    """Totoro bot subclass for added functionality"""

    discord.utils.setup_logging(level=logging.INFO)

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("t!"),
            help_command=commands.MinimalHelpCommand(),
            intents=discord.Intents.all(),
        )
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.config: TotoroConfigHandler = TotoroConfigHandler()
        self.node_pool = pomice.NodePool()
        self.owner_ids = set(self.config.get("owner_ids"))
        self.start_time = datetime.now()

    async def startup(self) -> None:
        """Startup method for the bot"""
        self.logger.info(f"Starting Totoro (PID {os.getpid()})")
        await self._load_extensions()
        await self.start(self.config.get("token"))

    async def _load_extensions(self) -> None:
        self.logger.info("Attempting to load cogs:")
        for ext in os.listdir("Totoro/cogs"):
            if ext.endswith(".py"):
                cog = f"cogs.{ext[:-3]}"
                try:
                    await self.load_extension(cog)
                    self.logger.info(f"{cog}... success")
                except commands.ExtensionError as e:
                    self.logger.warn(
                        f"{cog}... failure\n - {''.join(traceback.format_exception(e))}"
                    )

    async def _establish_lava_node(self) -> None:
        """Makes a connection to local lavalink node and adds to pomice's node pool"""
        self.logger.info("Initializing Lavalink Node Connection Pool")
        await self.node_pool.create_node(
            bot=self,
            host="127.0.0.1",
            port=2333,
            password="youshallnotpass",
            identifier="totoro-local",
            spotify_client_id=self.config.get("spotify_client_id", category="lavalink"),
            spotify_client_secret=self.config.get(
                "spotify_client_secret", category="lavalink"
            ),
        )

    async def close(self):
        self.logger.info("Shutting down Totoro now...")
        await self.node_pool.disconnect()
        await super().close()

    async def on_ready(self):
        self.logger.info(f"{self.user} is ready!")
