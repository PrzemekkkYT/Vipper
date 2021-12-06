from re import L
import discord
from discord.ext import commands
from discord.utils import find
import traceback, asyncio, youtube_dl, requests
from useful import translate

playqueue = {}
fullplayqueue = {}
fullplayqueueposition = {}

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format':"bestaudio", "skip_download":True, "noplaylist":True}
emojis = {"1️⃣": 0, "2️⃣": 1, "3️⃣": 2, "4️⃣": 3, "5️⃣": 4}

def musicEmbed(toEmbed):
    return discord.Embed(title=(toEmbed), color=0X00AAFF)

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            playqueue[guild.id] = []
            fullplayqueue[guild.id] = []
            fullplayqueueposition[guild.id] = 0
    
    @commands.command(aliases=["join"], brief="connect.brief", description="connect.description", usage="connect.usage")
    async def connect(self, ctx, arg=None):
        if arg==None:
            if (ctx.author.voice):
                if (ctx.voice_client):
                    if ctx.voice_client.channel.id is ctx.author.voice.channel.id:
                        await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "connect.alreadyconnected")))
                        return False
                    else:
                        await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.diffrentchannel")))
                        return False
                else:
                    await ctx.author.voice.channel.connect()
                    await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "connect.connected", [ctx.author.voice.channel.name])))
                    return True
            else:
                await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.notconnected")))
                return False
        elif arg.lower()=="force":
            if (ctx.author.voice):
                if (ctx.voice_client):
                    if ctx.voice_client.channel.id is ctx.author.voice.channel.id:
                        await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "connect.alreadyconnected")))
                        return False
                    else:
                        await ctx.voice_client.move_to(ctx.author.voice.channel)
                        await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "connect.forceconnect", [ctx.author.voice.channel.name])))
                        return False
                else:
                    await ctx.author.voice.channel.connect()
                    await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "connect.connected", [ctx.author.voice.channel.name])))
                    return True
            else:
                await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "connect.notconnected")))
                return False
    
    @commands.command(brief="leave.brief", description="leave.description", usage="leave.usage")
    async def leave(self, ctx):
        if (ctx.author.voice):
            if (ctx.voice_client):
                if ctx.voice_client.channel.id is ctx.author.voice.channel.id:
                    await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "leave.left", [ctx.voice_client.channel.name])))
                    await ctx.voice_client.disconnect()
                else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.diffrentchannel")))
            else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.notconnected")))
        else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.usernotconnected")))

    def song_search(self, src, single=True):
        if single:
            try:
                src = str(src).split('&', 1)[0]
                with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{src}", download=False)['entries'][0]
                    
                return {'source': info['formats'][0]['url'], 'title': info['title']}
            except Exception as inst:
                print("===========! ERROR BYQ !===========")
                print(inst)
                print("===========! ERROR BYQ !===========")
        else:
            try:
                with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                    infos = ydl.extract_info(f"ytsearch5:{src}", download=False)['entries']
                tracks = []
                for info in infos:
                    tracks.append({'source': info['formats'][0]['url'], 'title': info['title']})
                return tracks
            except Exception as inst:
                print("===========! ERROR BYQ !===========")
                print(inst)
                print("===========! ERROR BYQ !===========")

    async def play_next(self, vc, context):
        if playqueue[vc.guild.id]:
            del playqueue[vc.guild.id][0]
            fullplayqueueposition[vc.guild.id] += 1
            if len(playqueue[vc.guild.id]) > 0:
                vc.play(discord.FFmpegPCMAudio(playqueue[vc.guild.id][0]['source'], **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(Music.play_next(self, vc, context), vc.loop))
                await context.send(embed=musicEmbed(translate(context.guild.id, "playnext.nowplaying", [playqueue[vc.guild.id][0]['title']])))
                vc.is_playing()
            else:
                await context.send(embed=musicEmbed(translate(context.guild.id, "playnext.queueend")))
                time = 0
        while not vc.is_playing():
            await asyncio.sleep(1)
            time += 1
            if vc.is_playing() and not vc.is_paused():
                time = 0
            if time >= 600:
                await vc.disconnect()
                await context.send(embed=musicEmbed(translate(context.guild.id, "playnext.leaved")))
            if not vc.is_connected():
                break

    @commands.command(aliases=['p'], brief="play.brief", description="play.description", usage="play.usage")
    async def play(self, ctx, *, url=None):
        if url is not None:
            if ctx.voice_client and ctx.message.author.voice:
                vc = ctx.voice_client
                await vc.move_to(ctx.message.author.voice.channel)
            else:
                connection = await self.connect(ctx)
                if connection is not False:
                    vc = ctx.voice_client
                    print("CONNECTION: ",connection)
                else: return
            
            if not requests.get(f"https://www.youtube.com/oembed?format=json&url={url}"):
                songs = self.song_search(url, False)
                embed = discord.Embed(
                    title=translate(ctx.guild.id, "play.choicetitle"),
                    description=(
                        "\n".join(
                            f"**{i+1}.** {songs[i]['title']}"
                            for i in range(len(songs))
                        )
                    )
                )
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/640px-YouTube_full-color_icon_%282017%29.svg.png")
                msg = await ctx.send(embed=embed)
                for emoji in emojis:
                    await msg.add_reaction(emoji)
                    
                def check(reaction, user):
                    return user == ctx.message.author and (
                        str(reaction.emoji) == "1️⃣" or
                        str(reaction.emoji) == "2️⃣" or
                        str(reaction.emoji) == "3️⃣" or
                        str(reaction.emoji) == "4️⃣" or
                        str(reaction.emoji) == "5️⃣"
                    )
        
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await msg.delete()
                    await ctx.message.delete()
                    embed = musicEmbed(translate(ctx.guild.id, "play.notselected"))
                    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/640px-YouTube_full-color_icon_%282017%29.svg.png")
                    await ctx.send(embed=embed)
                else:
                    await msg.delete()
                    playqueue[ctx.guild.id].append(songs[emojis[reaction.emoji]])
                    fullplayqueue[ctx.guild.id].append(songs[emojis[reaction.emoji]])
                    if not vc.is_playing(): await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "play.nowplaying", [songs[emojis[reaction.emoji]]['title']])))
                
            else:
                song = self.song_search(url)
                playqueue[ctx.guild.id].append(song)
                fullplayqueue[ctx.guild.id].append(song)

            if playqueue[ctx.guild.id][-1] is not None:
                if not vc.is_playing():
                    vc.play(discord.FFmpegPCMAudio(playqueue[ctx.guild.id][0]['source'], **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(Music.play_next(self, vc, ctx), self.client.loop))
                    await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "play.nowplaying", [playqueue[vc.guild.id][0]['title']])))
                else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "play.queueadd", [playqueue[ctx.guild.id][-1]['title']])))
            else: await ctx.send(embed=discord.Embed(title=translate(ctx.guild.id, "play.playerror"), color=0xFF8800))
        else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "play.nolink")))

    @commands.command(brief="stop.brief", description="stop.description", usage="stop.usage")
    async def stop(self, ctx):
        global playqueue

        vc = ctx.voice_client
        if vc:
            if ctx.message.author.voice:
                if vc.channel.id == ctx.message.author.voice.channel.id:
                    vc.stop()
                    playqueue[ctx.guild.id] = []
                    await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "stop.stopped")))
                else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.diffrentchannel")))
            else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.usernotconnected")))
        else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.notconnected")))

    @commands.command(brief="skip.brief", description="skip.description", usage="skip.usage")
    async def skip(self, ctx):
        vc = ctx.voice_client
        if vc:
            if ctx.message.author.voice:
                if vc.channel.id == ctx.message.author.voice.channel.id:
                    if vc.is_playing():
                        vc.stop()
                        embed = discord.Embed(title=translate(ctx.guild.id, "skip.skipped", [playqueue[ctx.guild.id][0]['title']]), color=0x00AAFF)
                        await ctx.send(embed=embed)
                    else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "skip.stopped")))
                else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.diffrentchannel")))
            else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.usernotconnected")))
        else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.notconnected")))

    @commands.command(brief="pause.brief", description="pause.description", usage="pause.usage")
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc:
            if ctx.message.author.voice:
                if vc.channel.id == ctx.message.author.voice.channel.id:
                    if vc.is_playing():
                        vc.pause()
                        await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "pause.paused")))
                    else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "pause.alreadypaused")))
                else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.diffrentchannel")))
            else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.usernotconnected")))
        else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.notconnected")))

    @commands.command(brief="resume.brief", description="resume.description", usage="resume.usage")
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc:
            if ctx.message.author.voice:
                if vc.channel.id == ctx.message.author.voice.channel.id:
                    if vc.is_paused():
                        vc.resume()
                        await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "resume.resumed")))
                    else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "resume.alreadyplaying")))
                else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.diffrentchannel")))
            else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.usernotconnected")))
        else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "vc.notconnected")))

    @commands.command(aliases=['playqueue','musicqueue','vcqueue'], brief="queue.brief", description="queue.description", usage="queue.usage")
    async def queue(self, ctx):
        try:
            if not playqueue[ctx.guild.id] or len(playqueue[ctx.guild.id]) < 1:
                title = translate(ctx.guild.id, "queue.nosongs")
                description= translate(ctx.guild.id, "queue.advice")
            elif len(playqueue[ctx.guild.id]) <= 6 and len(playqueue[ctx.guild.id]) >=1:
                title = translate(ctx.guild.id, "queue.current", [playqueue[ctx.guild.id][0]['title']])
                description = translate(ctx.guild.id, "queue.toplay", [str(len(playqueue[ctx.guild.id])-1)])
                for i in range(1, len(playqueue[ctx.guild.id])):
                    if playqueue[ctx.guild.id][i] is not None:
                        description = description + ("\n• "+playqueue[ctx.guild.id][i]['title'])
                    else:
                        description = description + ("\n• ------------")
            else:
                title = translate(ctx.guild.id, "queue.current", [playqueue[ctx.guild.id][0]['title']])
                description = translate(ctx.guild.id, "queue.toplay", [str(len(playqueue[ctx.guild.id])-1)])
                for i in range(1,6):
                    if playqueue[ctx.guild.id][i] is not None:
                        description = description + ("\n• "+playqueue[ctx.guild.id][i]['title'])
                    else:
                        description = description + ("\n• ------------")
                description = description + ("\n• ........................................................................")
            embed = discord.Embed(title=title, description=description, color=0x00AAFF)
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/640px-YouTube_full-color_icon_%282017%29.svg.png")
            await ctx.send(embed=embed)
        except Exception as inst:
            print("===========! QUEUE EXCEPTION !===========")
            print(inst)
            print("===========! QUEUE TRACEBACK !===========")
            traceback.print_tb(inst.__traceback__)
            print("================! QUEUE !================")
    
    @commands.command(hidden=True)
    async def printqueue(self, ctx):
        print("\n====================================================================================\n")
        print(playqueue)
        
    def npq(self, pq):
        playqueue = pq
        
    @commands.command(hidden=True)
    async def interruptListening(self, ctx, url, playq=playqueue):
        if self.client.voice_clients:
            for clnt in self.client.voice_clients:
                playq[clnt.guild.id].insert(1, Music.song_search(Music, src=url))
                Music.npq(Music, playq)
                clnt.stop()
        else:
            vcs = []
            for guild in self.client.guilds:
                print("guild.id:",guild.id)
                vcs.append(find(lambda v: len(v.members)>0, guild.voice_channels))
            for vc in vcs:
                clnt = await vc.connect()
                playq[clnt.guild.id].insert(0, Music.song_search(Music, src=url))

                clnt.play(discord.FFmpegPCMAudio(playq[clnt.guild.id][0]['source'], **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(clnt.disconnect(), self.client.loop))

    @commands.command(brief="playlast.brief", description="playlast.description", usage="playlast.usage")
    async def playlast(self, ctx):
        if fullplayqueueposition[ctx.guild.id] >= 1:
            fullplayqueueposition[ctx.guild.id] -= 1
            playqueue[ctx.guild.id].insert(1, playqueue[ctx.guild.id][0])
            playqueue[ctx.guild.id].insert(1, fullplayqueue[ctx.guild.id][fullplayqueueposition[ctx.guild.id]])
            await self.skip(ctx)
            fullplayqueueposition[ctx.guild.id] -= 1
        else: await ctx.send(embed=musicEmbed(translate(ctx.guild.id, "playlast.nosongs")))

def setup(client):
    client.add_cog(Music(client))