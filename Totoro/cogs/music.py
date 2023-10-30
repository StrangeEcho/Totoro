import asyncio
from datetime import timedelta

import discord
import pomice
from core import TotoroBot
from discord.ext import commands
from discord.ui import Select, View
from utils import humanize_timedelta


class TotoroPlayer(pomice.Player):
    """Customer subclass of Pomice's Player class to add Queue functionality"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = pomice.Queue()

    @property
    def queue(self) -> pomice.Queue:
        """Pomice's implmentation of a queue system"""
        return self._queue


class SelectorView(View):
    def __init__(self):
        super().__init__(timeout=30)

    async def on_timeout(self) -> None:
        self.clear_items()


class TotoroTrackSelector(Select):
    def __init__(self, ctx: commands.Context, tracks: list[pomice.Track]):
        super().__init__(
            placeholder="Select 1 of 5 tracks",
        )
        self.ctx = ctx
        self.tracks = tracks
        for i, track in enumerate(tracks[:5], 1):
            self.add_option(
                label=f"{i}. {track.title[:50]}",
                description=f"From: {track.author}",
                value=i - 1,
            )

    async def callback(self, inter: discord.Interaction):
        await inter.response.defer()
        if inter.user.id != self.ctx.author.id:
            return await inter.response.send_message(
                "You are not able to select from this menu",
                ephemeral=True,
                delete_after=5,
            )
        player: TotoroPlayer = self.ctx.voice_client
        track: pomice.Track = self.tracks[int(self.values[0])]
        if player.current:
            player.queue.put(track)
            await inter.followup.send(f"Added {track.title} to the queue")
        else:
            await player.play(track)
            await inter.followup.send(f"Now playing {track.title}")


class Music(commands.Cog):
    def __init__(self, bot: TotoroBot):
        self.bot = bot
        if self.bot.node_pool.node_count == 0:
            asyncio.get_event_loop().create_task(self._establish_lava_node())

    async def _establish_lava_node(self) -> None:
        """Makes a connection to local lavalink node and adds to pomice's node pool"""
        await self.bot.wait_until_ready()
        await self.bot.node_pool.create_node(
            bot=self.bot,
            host="127.0.0.1",
            port=2333,
            password="youshallnotpass",
            identifier="totoro-local",
            spotify_client_id=self.bot.config.get("spotify_client_id"),
            spotify_client_secret=self.bot.config.get("spotify_client_secret"),
        )

    def convert_time(self, length: int) -> str:
        """Convert seconds/milliseconds to formatted timedelta object"""
        return humanize_timedelta(timedelta(milliseconds=length))

    @commands.Cog.listener("on_pomice_track_end")
    async def track_end(self, player: TotoroPlayer, track, _):
        """Plays next song in queue. If none, player will be destroyed"""
        try:
            await player.play(player.queue.get())
        except pomice.QueueEmpty:
            await player.disconnect()

    @commands.Cog.listener("on_pomice_track_stuck")
    async def track_stuck(self, player: TotoroPlayer, track, _):
        """Plays next song in queue if the previous one got stick. If none, player will be destroyed"""
        try:
            await player.play(player.queue.get())
        except pomice.QueueEmpty:
            await player.disconnect()

    @commands.command()
    async def connect(self, ctx: commands.Context):
        """Connect Totoro to a voice channel with TotoroPlayer instance"""
        if not ctx.author.voice:
            return await ctx.send(
                ":x: You're not in a Voice Channel. Join one and try again."
            )
        if ctx.voice_client:
            return await ctx.send("There is an active player already in this guild")
        channel = ctx.author.voice.channel
        await channel.connect(cls=TotoroPlayer, self_deaf=True)
        await ctx.send(f":white_check_mark: Joined channel {channel.name}")

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        """Play a song through the bot"""
        if not ctx.author.voice:
            return await ctx.send(
                ":x: You're not in a Voice Channel. Join one and try again."
            )
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect(cls=TotoroPlayer, self_deaf=True)
        player: TotoroPlayer = ctx.voice_client
        tracks = await player.get_tracks(query, ctx=ctx)
        if not tracks:
            return await ctx.send(":x: No tracks found with that query")
        if isinstance(tracks, pomice.Playlist):
            for track in tracks.tracks:
                player.queue.put(track)
            msg = await ctx.send(
                f":scroll: Enqueued {tracks.track_count} tracks to the queue"
            )
            if not player.current:
                track = player.queue.get()
                await player.play(track)
                await msg.reply(f":notes: Now playing {track.title}")
            return
        if len(tracks) == 1:
            track = tracks[0]
            player.queue.put(track)
            if not player.current:
                await player.play(player.queue.get())
            return await ctx.send(f":scroll: Enqueued {track.title}")
        await ctx.send(
            embed=discord.Embed(
                title=f"Results for query: {query}",
                description="Select 1 of 5 Tracks",
                color=discord.Color.green(),
            ).set_thumbnail(
                url="https://images.vexels.com/media/users/3/184267/isolated/preview/8ec63d26d98d295993e1b29d341f1502-music-beamed-notes-icon.png"
            ),
            view=SelectorView().add_item(TotoroTrackSelector(ctx, tracks)),
        )

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
        player: TotoroPlayer = ctx.voice_client
        if player:
            await player.set_pause(not player.is_paused)
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
            return await ctx.send(
                "There is currently no player or current track playing"
            )
        np = player.current
        await ctx.send(
            embed=discord.Embed(
                title=np.title,
                description=f"from: {np.author}",
                color=discord.Color.green(),
                url=np.uri,
            )
            .set_thumbnail(url=np.thumbnail)
            .set_footer(text=f"ID: {np.identifier}")
            .add_field(name="Requester", value=np.requester)
            .add_field(name="Length", value=self.convert_time(np.length, "ms"))
            .add_field(name="Filters", value=np.filters)
            .add_field(name="Seekable", value=np.is_seekable)
        )


async def setup(bot: TotoroBot):
    await bot.add_cog(Music(bot))
