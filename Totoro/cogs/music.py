from discord.ext import commands
from core import TotoroBot
from utils import humanize_timedelta
from discord.ui import Select, View
from typing import Optional
from datetime import timedelta

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
    
    @commands.command(aliases=["next"])
    async def skip(self, ctx: commands.Context):
        """Skip the current song"""
        player: TotoroPlayer = ctx.voice_client
        if player:
            await player.stop()
            if player.current:
                await ctx.send(f"Now playing {player.current.title}")
            return
        await ctx.send("No active player")
    
    @commands.command()
    async def pause(self, ctx: commands.Context):
        """Toggle the pause setting on the current player"""
        player: TotoroPlayer = await ctx.voice_client
        if player:
            await player.pause(not player.paused)
            return
        await ctx.send("No active player")
    
    @commands.command()
    async def volume(self, ctx: commands.Context, volume: int):
        if volume < 0 or volume > 100:
            return await ctx.send("Volume range must be within 0 and 100")
        player: TotoroPlayer = ctx.voice_client
        await player.set_volume(volume)
        await ctx.send(f"Set player volume to {volume}")
    
    @commands.command(aliases=["np"])
    async def nowplaying(self, ctx: commands.Context):
        player: TotoroPlayer = ctx.voice_client
        if not player or not player.current:
            return await ctx.send("There is currently no player or current track playing")
        np = player.current
        await ctx.send(
            embed=discord.Embed(
                title=np.title,
                url=np.uri,
                description=f"From: {np.author}",
                color=discord.Color.green()
            ).set_thumbnail(
                url=np.artwork_url
            ).add_field(
                name="Length",
                value=humanize_timedelta(timedelta(milliseconds=np.length), precise=True)
            ).add_field(
                name="Seekable",
                value=np.seekable
            )
        )

    @commands.command()
    async def nodestats(self, ctx: commands.Context):
        """Displays statistics about Totoro's connected Lavalink Node(s)"""
        embed = discord.Embed(title="Node Statistics", color=discord.Color.green())
        for node in self.bot.node_pool.nodes:
            nodestat = node.stats
            embed.add_field(
                name=f"Node: {node.label}",
                value=f"Uptime: {humanize_timedelta(nodestat.uptime)}\n"
                      f"CPU Load: {nodestat.cpu.lavalink_load}\n"
                      f"Player(s): {nodestat.player_count} | Active: {nodestat.playing_player_count}"
            )
        await ctx.send(embed=embed)



async def setup(bot: TotoroBot):
    await bot.add_cog(Music(bot))
