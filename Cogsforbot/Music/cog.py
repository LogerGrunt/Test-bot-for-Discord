import wavelink
import nextcord
import datetime
from nextcord.ext import commands

async def node_connect(self):
    await self.bot.wait_until_ready()
    await wavelink.NodePool.create_node(bot = self.bot, host='lavalinkinc.ml', port=443, password='incognito', https=True)

class Music(commands.Cog):
    """Play music right on Discord!"""
    COG_EMOJI = '🎶'
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(node_connect(self))
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node {node.identifier} is ready!")
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(player: wavelink.Player, track: wavelink.Track, reason):
        ctx = player.ctx
        vc = wavelink.Player

        #if vc.loop:
            #return await vc.play(track)

        if not player.queue.is_empty:
            next_song = vc.queue.get()
            await vc.play(next_song)
            await ctx.send(f"now playing {next_song.title}")
        else:
            await ctx.send("Queue is empty") 
    
    @commands.command()
    async def play(self, ctx: commands.Context, *, search: wavelink.YouTubeTrack):
        if not ctx.voice_client:
            return await ctx.send("There is nothing playing right now")
        elif not ctx.author.voice:
            return await ctx.send("Please join a Voice Channel first, and then type '&play <track>'")
        elif not ctx.author.voice == ctx.me.voice:
            return await ctx.send("Please join the same Voice Channel first, and then type '&play <track>'")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        if vc.queue.is_empty and not vc.is_playing:
            await vc.play(search)
            conversion = datetime.timedelta(seconds=search.duration)
            musicduration = str(conversion)
            musicembed = nextcord.Embed(title="Now Playing", description=f"Song: [{search.title}]({search.uri})\n Artist: `{search.author}`\n Duration: `{musicduration}`")
            musicembed.set_thumbnail(url=search.thumb)
            await ctx.send(embed=musicembed)
        else:
            await vc.queue.put_wait(search)
            await ctx.send(f"Added `{search.title}` to the queue :)")
        vc.ctx = ctx
        setattr(vc, "loop", False)

    @commands.command()
    async def pause(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("There is nothing playing right now")
        elif not ctx.author.voice:
            return await ctx.send("Please join a Voice Channel first, and then type '&pause'")
        elif not ctx.author.voice == ctx.me.voice:
            return await ctx.send("Please join the same Voice Channel first, and then type '&pause'")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        await vc.pause()
        await ctx.send("Pausing currently playing music...")
    
    @commands.command()
    async def resume(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("There is nothing playing right now")
        elif not ctx.author.voice:
            return await ctx.send("Please join a Voice Channel first, and then type '&resume'")
        elif not ctx.author.voice == ctx.me.voice:
            return await ctx.send("Please join the same Voice Channel first, and then type '&resume'")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        await vc.resume()
        await ctx.send("Resuming selected music...")
    
    @commands.command()
    async def stop(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("There is nothing playing right now")
        elif not ctx.author.voice:
            return await ctx.send("Please join a Voice Channel first, and then type '&stop'")
        elif not ctx.author.voice == ctx.me.voice:
            return await ctx.send("Please join the same Voice Channel first, and then type '&stop'")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        await vc.stop()
        await ctx.send("Stopping current song...")
    
    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("There is nothing playing right now")
        elif not ctx.author.voice:
            return await ctx.send("Please join a Voice Channel first, and then type '&disconnect'")
        elif not ctx.author.voice == ctx.me.voice:
            return await ctx.send("Please join the same Voice Channel first, and then type '&disconnect'")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        await vc.disconnect()
        await ctx.send("Disconnecting from Voice Channel...")
    
    @commands.command()
    async def volume(self, ctx: commands.Context, volumevalue = None):
        if not ctx.voice_client:
            return await ctx.send("There is nothing playing right now")
        elif not ctx.author.voice:
            return await ctx.send("Please join a Voice Channel first, and then type '&volume <value between 0-1000>'")
        elif not ctx.author.voice == ctx.me.voice:
            return await ctx.send("Please join the same Voice Channel first, and then type '&volume <value between 0-1000>'")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        await vc.set_volume(int(volumevalue))
        await ctx.send(f"Changing Volume to `{volumevalue}`...")
    
    @commands.command()
    async def loop(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("There is nothing playing right now")
        elif not ctx.author.voice:
            return await ctx.send("Please join a Voice Channel first, and then type '&loop'")
        elif not ctx.author.voice == ctx.me.voice:
            return await ctx.send("Please join the same Voice Channel first, and then type '&loop'")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        try:
            vc.loop ^= True
        except:
            setattr(vc, "loop", False)
        
        if vc.loop:
            return await ctx.send("Loop is now enabled!")
        else:
            return await ctx.send("Loop is now disabled!")
    
    @commands.command()
    async def queue(self, ctx: commands.Context):
        if not ctx.voice_client:
            return await ctx.send("There is nothing playing right now")
        elif not ctx.author.voice:
            return await ctx.send("Please join a Voice Channel first, and then type '&queue'")
        elif not ctx.author.voice == ctx.me.voice:
            return await ctx.send("Please join the same Voice Channel first, and then type '&queue'")
        else:
            vc: wavelink.Player = ctx.voice_client
        
        if vc.queue.is_empty:
            return await ctx.send("Queue is empty!")
        
        em = nextcord.Embed(title="Queue")
        queue = vc.queue.copy()
        song_count = 0
        for song in queue:
            song_count += 1
            em.add_field(name=f"Song Num {song_count}", value=f"`{song.title}`")
        
        return await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Music(bot))