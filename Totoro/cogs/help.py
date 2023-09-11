from discord.ext import commands
from core import TotoroBot

import platform
import discord

class TotoroHelpCommand(commands.HelpCommand):
    """Custom help command for Totoro"""
    
    async def send_bot_help(self, _):
        bot = self.context.bot
    
        await self.get_destination().send(
            embed=discord.Embed(
                title=":wave: Hello there I am Totoro",
                description="Totoro is a personal music/utility bot that ruben made for sum reason\n"
                            f"**[Library Ver]** __Discord.py__: `{discord.__version__}`\n"
                            f"**[Language Ver]** __Python__: `{platform.python_version()}`\n"
                            f"Commands: `{len(bot.commands)}` Modules: `{len(bot.cogs)}`"
            ).add_field(
                name="Module List",
                value="\n".join([f"`{cog}`" for cog in bot.cogs])
            ).set_footer(
                text="Use t!help <command/module>",
                icon_url=self.context.author.display_avatar.url
            ).set_thumbnail(
                url=bot.user.display_avatar.url
            )
        )

class Help(commands.Cog):
    def __init__(self, bot: TotoroBot):
        bot.help_command = TotoroHelpCommand()
    
async def setup(bot: TotoroBot):
    await bot.add_cog(Help(bot))
