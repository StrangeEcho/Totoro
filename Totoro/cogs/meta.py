from discord.ext import commands
from core import TotoroBot

import discord


class Meta(commands.Cog):
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
        


async def setup(bot: TotoroBot):
    await bot.add_cog(Meta(bot))
