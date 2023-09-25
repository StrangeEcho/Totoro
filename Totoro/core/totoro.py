from discord.ext import commands
from typing import Any, Optional

import traceback
import os
import tomllib
import logging
import discord
import mafic


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
        self.node_pool = mafic.NodePool(self)
        self.owner_ids = set(self.config.get("owner_ids"))

    async def startup(self) -> None:
        """Startup method for the bot"""
        self.logger.info("Starting Totoro login process...")
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
                    self.logger.warn(f"{cog}... failure\n - {''.join(traceback.format_exception(e))}")

    async def _establish_lava_node(self) -> None:
        """Makes a connection to local lavalink node and adds to mafic's node pool"""
        self.logger.info("Initializing Mafic NodePool")
        try:
            node = await self.node_pool.create_node(
                host="127.0.0.1",
                port=2333,
                password="youshallnotpass",
                label="totoroMAIN",
            )
        except RuntimeError as e:
            self.logger.warn(
                "Failed Initializing Lavalink connection | Unloading Music module recommended\n"
                f"Error:\n{''.join(traceback.format_exception(e))}"
            )

    async def close(self):
        self.logger.info("Shutting down Totoro now...")
        self.logger.info("Closing Mafic Lavalink connection pool")
        await self.node_pool.close()
        await super().close()

    async def on_ready(self):
        self.logger.info(f"{self.user} is ready!")
        await self._establish_lava_node()

    async def on_connect(self):
        self.logger.info("All Shard Connections Established...")
