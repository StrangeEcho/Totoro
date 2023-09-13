from discord.ext import commands
from core import TotoroBot
from discord.ui import Select, View
from typing import Optional

import mafic
import discord


class TotoroPlayer(mafic.Player):
    """Customer subclass of Mafic's Player class to add Queue functionality"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue: list[mafic.Track] = []

    @property
    def queue(self) -> list[mafic.Track]:
        """list object representing a music queue"""
        return self._queue


class TotoroTrackSelector(Select):
    def __init__(self, ctx: commands.Context, tracks: list[mafic.Track]):
        super().__init__(
            placeholder="Select 1 of 5 tracks",
        )
        self.ctx = ctx
        self.tracks = tracks
        for i, track in enumerate(tracks, 1):
            self.add_option(
                label=f"{i}. {track.title[:50]}",
                description=f"From: {track.author}",
                value=i - 1,
            )

    async def callback(self, inter: discord.Interaction):
        if inter.user.id != self.ctx.author.id:
            return await inter.response.send_message(
                "You are not able to select from this menu",
                ephemeral=True,
                delete_after=5,
            )
        player: TotoroPlayer = self.ctx.voice_client
        track: mafic.Track = self.tracks[self.values[0]]
        if not player.current:
            await player.play(track)
            await self.ctx.send(f"Now playing: {track.title}")
            return
        player.queue.append(track)
        await self.ctx.send(f"Added {track.title} to the queue")


class Music(commands.Cog):
    def __init__(self, bot: TotoroBot):
        self.bot = bot

    async def connect_vc(self, ctx: commands.Context) -> Optional[discord.Message]:
        """Voice channel connection handler"""
        if not ctx.author.voice:
            return await ctx.send(
                "You're not in a Voice Channel. Join one and try again."
            )
        if ctx.voice_client:
            return await ctx.send("There is an active player already in this guild")
        channel = ctx.author.voice.channel
        await channel.connect(cls=TotoroPlayer, self_deaf=True)
        await ctx.send(f"Joined channel {channel.name}")

    @commands.Cog.listener("on_track_end")
    async def track_end(self, event: mafic.TrackEndEvent):
        """Plays next song in queue. If none, player will destroyed"""
        player: TotoroPlayer = event.player
        try:
            await player.play(player.queue.pop(0))
        except IndexError:
            await player.disconnect()

    @commands.Cog.listener("on_track_stuck")
    async def track_stuck(self, event: mafic.TrackStuckEvent):
        """Plays next song in queue if the previous one got stick. If none, player will destroyed"""
        player: TotoroPlayer = event.player
        try:
            await player.play(player.queue.pop(0))
        except IndexError:
            await player.disconnect()

    @commands.command()
    async def connect(self, ctx: commands.Context):
        """Connect Totoro to a voice channel with TotoroPlayer instance"""
        await self.connect_vc(ctx)

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        """Play a song through the bot"""
        player: TotoroPlayer = ctx.voice_client
        if not player:
            return await ctx.send(
                f"No active player. Run command `{ctx.clean_prefix}connect` to start one"
            )
        track = (await player.fetch_tracks(query))[0]
        if player.current:
            player.queue.append(track)
            return await ctx.send(f"Added {track.title} to queue")
        await player.play(track)
        await ctx.send(f"Now playing {track.title}")

    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        """Disconnect the current voice player"""
        player: TotoroPlayer = ctx.voice_client
        if player:
            await player.disconnect()
            return
        await ctx.send("No active player")


async def setup(bot: TotoroBot):
    await bot.add_cog(Music(bot))
