import discord
from core import TotoroBot
from discord.ext import commands


class TotoroHelpCommand(commands.HelpCommand):
    """Custom help command for Totoro"""

    async def send_bot_help(self, _):
        bot = self.context.bot
        await self.get_destination().send(
            embed=discord.Embed(
                title=":wave: Hi there I am Totoro",
                description="I am a private music/utility bot based off the movie My Neighbor Totoro. uhhhhhhh- and thats basically all",
                color=discord.Color.green(),
            )
            .add_field(
                name="Module List", value="\n".join([f"`{cog}`" for cog in bot.cogs])
            )
            .set_footer(
                text="Use t!help <command/module>",
                icon_url=self.context.author.display_avatar.url,
            )
            .set_thumbnail(url=bot.user.display_avatar.url)
        )

    async def send_cog_help(self, cog: commands.Cog):
        bot = self.context.bot
        await self.get_destination().send(
            embed=discord.Embed(
                title=f"Module: `{cog.qualified_name}`",
                description=cog.description,
                color=discord.Color.green(),
            )
            .add_field(
                name=f"Commands({len(cog.get_commands())}):",
                value=", ".join([f"`{cmd}`" for cmd in cog.get_commands()]),
            )
            .set_thumbnail(url=bot.user.display_avatar.url)
            .set_footer(
                icon_url=self.context.author.display_avatar.url,
                text="Do t!help <cmd> to get more info on a specific command",
            )
        )

    async def send_command_help(self, cmd: commands.Command):
        aliases = cmd.aliases
        cd = cmd._buckets._cooldown
        embed = discord.Embed(
            title=f"Command: `{cmd.qualified_name}`",
            description=cmd.description,
            color=discord.Color.green(),
        ).add_field(name="Module", value=f"`{cmd.cog_name}`")
        if cd:
            embed.add_field(
                name="Cooldown",
                value=f"Rate: {cd.rate} | Cooldown(in seconds): {cd.per}",
            )
        if aliases:
            embed.add_field(name="Aliases", value="\n".join(aliases))
        await self.get_destination().send(embed=embed)


class Help(commands.Cog):
    def __init__(self, bot: TotoroBot):
        bot.help_command = TotoroHelpCommand()


async def setup(bot: TotoroBot):
    await bot.add_cog(Help(bot))
