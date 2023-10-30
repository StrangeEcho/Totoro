import logging
import os
import tomllib
import traceback
from datetime import datetime
from typing import Any, Optional

import discord
import pomice
from discord.ext import commands


class TotoroConfigHandler:
    """A simple config helper for Totoro"""

    with open("./Totoro/core/config.toml", "rb") as confile:
        config: dict[Any, Any] = tomllib.load(confile)

    def get(self, config_name: str) -> Any:
        """Fetch specified config from config.toml file"""
        return self.config.get(config_name) # Returns None if no config found


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

    async def on_command_error(
        self, ctx: commands.Context, exception: commands.CommandError
    ):
        self.logger.error(f"Unhandled Exception Caught:\n{''.join(traceback.format_exception(exception))}")

    async def close(self):
        self.logger.info("Shutting down Totoro now...")
        await self.node_pool.disconnect()
        await super().close()

    async def on_ready(self):
        self.logger.info(f"{self.user} is ready!")
