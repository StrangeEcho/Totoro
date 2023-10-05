from discord.ext import commands
from core import TotoroBot

import platform
import discord


class Meta(commands.Cog):
    """Commands more related to the Totoro itself"""

    def __init__(self, bot: TotoroBot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx: commands.Context):
        """Logout/Close the bot process"""
        await ctx.send("Logging out now...")
        await self.bot.close()

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
            .set_thumbnail(url=self.bot.user.display_avatar.url)
            .set_footer(
                text=f"This bot was made using discord.py {discord.__version__} and Python version {platform.python_version()}",
                icon_url=ctx.author.display_avatar.url,
            )
            .add_field(
                name="Guilds | Users",
                value=f"Guilds: {len(self.bot.guilds)} | Users: {len(self.bot.users)}",
            )
            .add_field(
                name="Uptime", value=discord.utils.format_dt(self.bot.start_time, "R")
            )
            .add_field(
                name="Owner(s)",
                value="\n".join(
                    [str(self.bot.get_user(oid)) for oid in self.bot.owner_ids]
                ),
            )
            .add_field(
                name="Cogs | Commands",
                value=f"Cogs: {len(self.bot.cogs)} | Commands: {len(self.bot.commands)}",
            )
            .add_field(
                name="Latency",
                value=f"{round(self.bot.latency * 1000)}ms",
                inline=False,
            )
        )


async def setup(bot: TotoroBot):
    await bot.add_cog(Meta(bot))
