from discord.ext import commands
from typing import Any, Optional

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
            command_prefix="t!",
            help_command=commands.MinimalHelpCommand(),
            intents=discord.Intents.all(),
        )
        self.logger: logging.Logger = logging.getLogger("totoro-main")
        self.config: TotoroConfigHandler = TotoroConfigHandler()
        self.nodepool: pomice.NodePool = pomice.NodePool()

    async def startup(self):
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
                    self.logger.warn(f"{cog}... failure\n - {e}")

    async def on_ready(self):
        self.logger.info(f"{self.user} is ready!")
