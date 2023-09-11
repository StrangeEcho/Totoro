from discord.ext import commands
from core import TotoroBot

import pomice
import logging
import asyncio


class Player(pomice.Player):
    """Custom implementation of pomice's player adding a queue system"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = pomice.Queue()

    @property
    def queue(self) -> pomice.Queue:
        return self._queue


class Music(commands.Cog):
    def __init__(self, bot: TotoroBot):
        self.bot = bot
        self.music_logger = logging.getLogger("music-master")

    async def create_ll_connection(self) -> None:
        """Create a connection to LavaLink node"""
        await self.bot.wait_until_ready()
        try:
            node = await self.bot.nodepool.create_node(
                bot=self.bot,
                host=self.bot.config.get("host", category="lavalink"),
                port=self.bot.config.get("port", category="lavalink"),
                password=self.bot.config.get("password", category="lavalink"),
                spotify_client_id=self.bot.config.get(
                    "spotify_client_id", category="lavalink"
                ),
                spotify_client_secret=self.bot.config.get(
                    "spotify_client_secret", category="lavalink"
                ),
                identifier="MAIN",
            )
            self.music_logger.info(f"Connected Lavalink Node: {node._identifier}")
        except (pomice.NodeConnectionFailure, pomice.NodeCreationError) as e:
            self.music_logger.warn(
                f"Failed connecting Lavalink node.\nError info: {e}\n\nUnloading..."
            )
            await self.cog_unload()
    
    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: Player, track: pomice.Track):
        """Skip/Destroy player when a track ends"""
        try:
            await player.play(player.queue.get())
        except pomice.QueueEmpty:
            await asyncio.sleep(
                60
            )  # wait 1 min to see if they play any music before queue gets destroyed
            if not player.current and not player.queue:
                await player.destroy()

    @commands.Cog.listener()
    async def on_pomice_track_stuck(self, player: Player, track, _):
        try:
            await player.play(player.queue.get())
        except pomice.QueueEmpty:
            await player.destroy()

    @commands.Cog.listener()
    async def on_pomice_track_exception(self, player: Player, track, _):
        try:
            await player.play(player.queue.get())
        except pomice.QueueEmpty:
            await player.destroy()

    @commands.command()
    async def connect(self, ctx: commands.Context):
        """Connect the bot to a VC to start playing music"""
        await ctx.author.voice.channel.connect(cls=Player)
        await ctx.send(f"Joined `{ctx.author.voice.channel.name}`")


async def setup(bot: TotoroBot):
    await bot.add_cog(Music(bot))
