from discord.ext import commands
from core import TotoroBot

import platform
import discord


class Meta(commands.Cog):
    """Commands more related to the Totoro itself"""

    def __init__(self, bot: TotoroBot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Return the Gateway/WS connection latency"""
        msg = await ctx.send("Measuring Latency...")
        msg_latency = round(
            (msg.created_at - ctx.message.created_at).total_seconds() * 1000
        )
        await msg.edit(
            embed=discord.Embed(
                title="Totoro's Latency",
                description=f"WebSocket/Gateway: {round(self.bot.latency* 1000)}ms\nMessage: {msg_latency}ms",
                color=discord.Color.green(),
            )
        )

    @commands.command()
    async def info(self, ctx: commands.Context):
        """Information about the bot itself"""
        await ctx.send(
            embed=discord.Embed(
                title="Hi again! Heres sum info about me",
                description="First and foremost [this](https://github.com/Yat-o/Totoro) right here is my source code",
                color=discord.Color.green(),
            )
            .add_field(name="Cached Users", value=f"`{len(self.bot.users)}`")
            .add_field(
                name="Commands/Modules",
                value=f"I currently have `{len(self.bot.commands)}` commands and `{len(self.bot.cogs)}` modules",
            )
            .add_field(
                name="Recognized Ownership ID(s)",
                value="\n".join(self.bot.owner_ids) or self.bot.owner_id,
            )
            .add_field(
                name="Misc",
                value=f"Discord.py Version: `{discord.__version__}`\nPython Version: `{platform.python_version()}`",
            )
        )

    @commands.command()
    async def say(self, ctx: commands.Context, *, msg):
        """Make the bot say sum"""
        await ctx.send(msg)


async def setup(bot: TotoroBot):
    await bot.add_cog(Meta(bot))
