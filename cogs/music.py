import discord
from discord.ext import commands
from discord.utils import find
import traceback, asyncio, youtube_dl

playqueue = {}
playcontext = {}

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format':"bestaudio"}

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            playqueue[guild.id] = []
            
    def musicEmbed(self, toEmbed):
        return discord.Embed(title=(toEmbed), color=0X00AAFF)
    
    @commands.command(aliases=["join"], brief="Łączy bota z czatem głosowym", description="Umożliwia połączenie bota z czatem głosowym w celu późniejszego odtwarzania muzyki", usage="v!connect")
    async def connect(self, ctx, arg=None):
        if arg==None:
            if (ctx.author.voice):
                if (ctx.voice_client):
                    if ctx.voice_client.channel.id is ctx.author.voice.channel.id:
                        await ctx.send(embed=self.musicEmbed("Bot jest już połączony z kanałem na którym znajduje się użytkownik"))
                        return False
                    else:
                        await ctx.send(embed=self.musicEmbed("Bot znajduje się na innym kanale niż użytkownik"))
                        return False
                else:
                    await ctx.author.voice.channel.connect()
                    await ctx.send(embed=self.musicEmbed(f"Połączono z kanałem głosowym {ctx.author.voice.channel.name}!"))
                    return True
            else:
                await ctx.send(embed=self.musicEmbed("Użytkownik nie jest połączony z żadnym kanałem głosowym"))
                return False
        elif arg.lower()=="force":
            if (ctx.author.voice):
                if (ctx.voice_client):
                    if ctx.voice_client.channel.id is ctx.author.voice.channel.id:
                        await ctx.send(embed=self.musicEmbed("Bot jest już połączony z kanałem na którym znajduje się użytkownik"))
                        return False
                    else:
                        await ctx.voice_client.move_to(ctx.author.voice.channel)
                        await ctx.send(embed=self.musicEmbed(f"Wymuszono przeniesienie bota na kanał {ctx.author.voice.channel.name}"))
                        return False
                else:
                    await ctx.author.voice.channel.connect()
                    await ctx.send(embed=self.musicEmbed(f"Połączono z kanałem głosowym {ctx.author.voice.channel.name}!"))
                    return True
            else:
                await ctx.send(embed=self.musicEmbed("Użytkownik nie jest połączony z żadnym kanałem głosowym"))
                return False
    
    @commands.command(brief="Wyrzuca bota z kanału głosowego", desciption="Umożlwia wyrzucenie bota z kanału głosowego, jeżeli nie jest już potrzebny", usage="v!leave")
    async def leave(self, ctx):
        if (ctx.author.voice):
            if (ctx.voice_client):
                if ctx.voice_client.channel.id is ctx.author.voice.channel.id:
                    await ctx.send(embed=self.musicEmbed(f"Opuszczono kanał głosowy {ctx.voice_client.channel.name}!"))
                    await ctx.voice_client.disconnect()
                else: await ctx.send(embed=self.musicEmbed("Bot znajduje się na innym kanale niż użytkownik!"))
            else: await ctx.send(embed=self.musicEmbed("Bot nie jest połączony z żadnym kanałem głosowym!"))
        else: await ctx.send(embed=self.musicEmbed("Użytkownik nie jest połączony z żadnym kanałem głosowym!"))

    def song_search(self, src):
        try:
            with youtube_dl.YoutubeDL(YDL_OPTIONS ) as ydl:
                info = ydl.extract_info(f"ytsearch:{src}", download=False)['entries'][0]
                
            return {'source': info['formats'][0]['url'], 'title': info['title']}
        except Exception as inst:
            print("===========! ERROR BYQ !===========")
            print(inst)
            print("===========! ERROR BYQ !===========")

    async def play_next(self, vc, context):
        if playqueue[vc.guild.id]:
            del playqueue[vc.guild.id][0]
            if len(playqueue[vc.guild.id]) > 0:
                vc.play(discord.FFmpegPCMAudio(playqueue[vc.guild.id][0]['source'], **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(Music.play_next(self, vc, context), vc.loop))
                await context.send(embed=self.musicEmbed("Odtwarzam: "+playqueue[vc.guild.id][0]['title']))
                vc.is_playing()
            else:
                await context.send(embed=self.musicEmbed("Zakończono kolejkę"))

    @commands.command(brief="Służy do odtwarzania muzyki", description="Służy do odtwarzania muzyki z platformy YouTube używając linka do wideo jako argumentu (nie każde wideo zadziała)", usage="v!play <youtube url>")
    async def play(self, ctx, url=None):
        if url is not None:
            print(f"playcontext1: {playcontext}")
            playcontext[ctx.guild.id] = ctx
            print(f"playcontext2: {playcontext}")
            if ctx.voice_client and ctx.message.author.voice:
                vc = ctx.voice_client
                await vc.move_to(ctx.message.author.voice.channel)
            else:
                connection = await self.connect(ctx)
                if connection is not False:
                    vc = ctx.voice_client
                    print("CONNECTION: ",connection)
                else: return
            
            song = self.song_search(url)
            playqueue[ctx.guild.id].append(song)

            if playqueue[ctx.guild.id][-1] is not None:
                if not vc.is_playing():
                    vc.play(discord.FFmpegPCMAudio(playqueue[ctx.guild.id][0]['source'], **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(Music.play_next(self, vc, ctx), self.client.loop))
                    #vc.is_playing()
                else: await ctx.send(embed=self.musicEmbed("Dodano \""+playqueue[ctx.guild.id][-1]['title']+"\" do kolejki!"))
            else: await ctx.send(embed=discord.Embed(title="Nie udało się użyć tego wideo, spróbuj z innym!", color=0xFF8800))
        else: await ctx.send(embed=self.musicEmbed("Nie podano linku!"))

    @commands.command(brief="Zatrzymuje muzykę i czyści kolejkę", description="Zatrzymuję muzykę i czyści kolejkę, np. w celu stworzenia nowej kolejki do odtworzenia", usage="v!stop")
    async def stop(self, ctx):
        global playqueue

        vc = ctx.voice_client
        if vc:
            if ctx.message.author.voice:
                if vc.channel.id == ctx.message.author.voice.channel.id:
                    vc.stop()
                    playqueue[ctx.guild.id] = []
                    await ctx.send(embed=self.musicEmbed("Zakończono odtwarzanie muzyki oraz wyczyszczono kolejkę"))
                else: await ctx.send(embed=self.musicEmbed("Bot znajduje się na innym kanale!"))
            else: await ctx.send(embed=self.musicEmbed("Nie znajdujesz się na żadnym kanale głosowym!"))
        else: await ctx.send(embed=self.musicEmbed("Bot nie jest połączony z żadnym kanałem głosowym!"))

    @commands.command(brief="Pomija aktualnie odtwarzaną muzyke", description="Pomija aktualnie odtwarzaną muzykę i odtwarza następną z kolejki, jeżeli takowa znajduje się w kolejce", usage="v!skip")
    async def skip(self, ctx):
        vc = ctx.voice_client
        if vc:
            if ctx.message.author.voice:
                if vc.channel.id == ctx.message.author.voice.channel.id:
                    if vc.is_playing():
                        vc.stop()
                        embed = discord.Embed(title=f"Pominięto {playqueue[ctx.guild.id][0]['title']}", color=0x00AAFF)
                        await ctx.send(embed=embed)
                    else: await ctx.send(embed=self.musicEmbed("Muzyka jest już zatrzymana!"))
                else: await ctx.send(embed=self.musicEmbed("Bot znajduje się na innym kanale!"))
            else: await ctx.send(embed=self.musicEmbed("Nie znajdujesz się na żadnym kanale głosowym!"))
        else: await ctx.send(embed=self.musicEmbed("Bot nie jest połączony z żadnym kanałem głosowym!"))

    @commands.command(brief="Zatrzymuje aktualnie odtwarzaną muzykę", description="Zatrzymuje aktualnie odtwarzaną muzyke z możliwością wznowienia jej od tego samego momentu", usage="v!pause")
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc:
            if ctx.message.author.voice:
                if vc.channel.id == ctx.message.author.voice.channel.id:
                    if vc.is_playing():
                        vc.pause()
                        await ctx.send(embed=self.musicEmbed("Zatrzymano muzykę! Możesz wznowić komendą: v!resume"))
                    else: await ctx.send(embed=self.musicEmbed("Muzyka jest już zatrzymana!"))
                else: await ctx.send(embed=self.musicEmbed("Bot znajduje się na innym kanale!"))
            else: await ctx.send(embed=self.musicEmbed("Nie znajdujesz się na żadnym kanale głosowym!"))
        else: await ctx.send(embed=self.musicEmbed("Bot nie jest połączony z żadnym kanałem głosowym!"))

    @commands.command(brief="Wznawia zatrzymaną muzykę", description="Wznawia zatrzymaną muzykę od momentu w którym została zatrzymana", usage="v!resume")
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc:
            if ctx.message.author.voice:
                if vc.channel.id == ctx.message.author.voice.channel.id:
                    if vc.is_paused():
                        vc.resume()
                        await ctx.send(embed=self.musicEmbed("Wznowiono odtwarzanie muzyki"))
                    else: await ctx.send(embed=self.musicEmbed("Muzyka jest już odtwarzana!"))
                else: await ctx.send(embed=self.musicEmbed("Bot znajduje się na innym kanale!"))
            else: await ctx.send(embed=self.musicEmbed("Nie znajdujesz się na żadnym kanale głosowym!"))
        else: await ctx.send(embed=self.musicEmbed("Bot nie jest połączony z żadnym kanałe glosowym!"))

    @commands.command(aliases=['playqueue','musicqueue','vcqueue'], brief="Wyświetla kolejkę odtwarzania", description="Wyświetla 5 następnych piosenek do odtworzenia z kolejki", usage="v!queue")
    async def queue(self, ctx):
        try:
            if not playqueue[ctx.guild.id] or len(playqueue[ctx.guild.id]) < 1:
                title = "Brak piosenek w kolejce"
                description="Możesz dodać jakieś komendą v!play (link)"
            elif len(playqueue[ctx.guild.id]) <= 6 and len(playqueue[ctx.guild.id]) >=1:
                title = ("Aktualnie odtwarzane:\n"+playqueue[ctx.guild.id][0]['title'])
                description = (str(len(playqueue[ctx.guild.id])-1)+" piosenek do odtworzenia")
                for i in range(1, len(playqueue[ctx.guild.id])):
                    if playqueue[ctx.guild.id][i] is not None:
                        description = description + ("\n• "+playqueue[ctx.guild.id][i]['title'])
                    else:
                        description = description + ("\n• ------------")
            else:
                title = ("Aktualnie odtwarzane:\n"+playqueue[ctx.guild.id][0]['title'])
                description = (str(len(playqueue[ctx.guild.id])-1)+" piosenek do odtworzenia")
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
    
    @commands.command()
    async def printqueue(self, ctx):
        print("\n====================================================================================\n")
        print(playqueue)
        
    def npq(self, pq):
        playqueue = pq
        
    @commands.command()
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
                clnt.play(discord.FFmpegPCMAudio(playq[clnt.guild.id][0]['source'], **FFMPEG_OPTIONS))

def setup(client):
    client.add_cog(Music(client))