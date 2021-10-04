import discord
from discord.ext import commands
import traceback, asyncio, youtube_dl

playqueue = []
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format':"bestaudio"}

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="Łączy bota z czatem głosowym", description="Umożliwia połączenie bota z czatem głosowym w celu późniejszego odtwarzania muzyki", usage="v!connect")
    async def connect(self, ctx):
        if (ctx.author.voice):
            channel = ctx.message.author.voice.channel
            await channel.connect()
            await ctx.send("Połączono z kanałem głosowym "+channel.name)
            return True
        else:
            await ctx.send("Użytkownik nie jest połączony z żadnym kanałem głosowym")
            return False

    @commands.command(brief="Wyrzuca bota z kanału głosowego", desciption="Umożlwia wyrzucenie bota z kanału głosowego, jeżeli nie jest już potrzebny", usage="v!leave")
    async def leave(self, ctx):
        if (ctx.voice_client):
            await ctx.send("Opuszczono kanał głosowy")
            await ctx.guild.voice_client.disconnect()
        else:
            await ctx.send("Bot nie jest połączony z żadnym kanałem głosowym")

    def song_search(self, src):
        try:
            with youtube_dl.YoutubeDL(YDL_OPTIONS ) as ydl:
                info = ydl.extract_info(f"ytsearch:{src}", download=False)['entries'][0]
                
            return {'source': info['formats'][0]['url'], 'title': info['title']}
        except Exception as inst:
            print("===========! ERROR BYQ !===========")
            print(inst)
            print("===========! ERROR BYQ !===========")

    async def play_next(self, ctx):
        vc = ctx.voice_client
        if playqueue:
            del playqueue[0]
            if len(playqueue) > 0:
                vc.play(discord.FFmpegPCMAudio(playqueue[0]['source'], **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(Music.play_next(self, ctx), self.client.loop))
                embed = discord.Embed(title=("Odtwarzam: "+playqueue[0]['title']), color=0X00AAFF)
                await ctx.send(embed=embed)
                vc.is_playing()
            else:
                embed = discord.Embed(title="Zakończono kolejkę", color=0x00AAFF)
                await ctx.send(embed=embed)

    @commands.command(brief="Służy do odtwarzania muzyki", description="Służy do odtwarzania muzyki z platformy YouTube używając linka do wideo jako argumentu (nie każde wideo zadziała)", usage="v!play <youtube url>")
    async def play(self, ctx, url=None):
        if url is not None:
            if ctx.voice_client and ctx.message.author.voice:
                vc = ctx.voice_client
                await vc.move_to(ctx.message.author.voice.channel)
            else:
                connection = await Music.connect(self, ctx)
                if connection is not False:
                    vc = ctx.voice_client
                    print("CONNECTION: ",connection)
                else: return
            
            song = Music.song_search(self, url)
            playqueue.append(song)

            if playqueue[-1] is not None:
                if not vc.is_playing():
                    vc.play(discord.FFmpegPCMAudio(playqueue[0]['source'], **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(Music.play_next(self, ctx), self.client.loop))
                    vc.is_playing()
                else:
                    queueembed = discord.Embed(title=("Dodano \""+playqueue[-1]['title']+"\" do kolejki"), color=0x00AAFF)
                    await ctx.send(embed=queueembed)
            else:
                errorembed = discord.Embed(title="Nie udało się użyć tego wideo, spróbuj z innym", color=0xFF8800)
                await ctx.send(embed=errorembed)
        else: await ctx.send("Nie podano linku")

    @commands.command(brief="Zatrzymuje muzykę i czyści kolejkę", description="Zatrzymuję muzykę i czyści kolejkę, np. w celu stworzenia nowej kolejki do odtworzenia", usage="v!stop")
    async def stop(self, ctx):
        global playqueue

        vc = ctx.voice_client
        if vc:
            await vc.move_to(ctx.message.author.voice.channel)
        else:
            await Music.connect(self, ctx)
            vc = ctx.voice_client
        vc.stop()
        playqueue = []
        embed = discord.Embed(title="Zakończono odtwarzanie muzyki oraz wyczyszczono kolejkę", color=0x00AAFF)
        await ctx.send(embed=embed)

    @commands.command(brief="Pomija aktualnie odtwarzaną muzyke", description="Pomija aktualnie odtwarzaną muzykę i odtwarza następną z kolejki, jeżeli takowa znajduje się w kolejce", usage="v!skip")
    async def skip(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.move_to(ctx.message.author.voice.channel)
        else:
            await Music.connect(self, ctx)
            vc = ctx.voice_client
        embed = discord.Embed(title=("Pominięto "+playqueue[0]['title']), color=0x00AAFF)
        vc.stop()
        await ctx.send(embed=embed)

    @commands.command(brief="Zatrzymuje aktualnie odtwarzaną muzykę", description="Zatrzymuje aktualnie odtwarzaną muzyke z możliwością wznowienia jej od tego samego momentu", usage="v!pause")
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.move_to(ctx.message.author.voice.channel)
        else:
            await Music.connect(self, ctx)
            vc = ctx.voice_client
        vc.pause()
        embed = discord.Embed(title="Zatrzymano muzykę! Możesz wznowić komendą: v!resume", color=0x00AAFF)
        await ctx.send(embed=embed)

    @commands.command(brief="Wznawia zatrzymaną muzykę", description="Wznawia zatrzymaną muzykę od momentu w którym została zatrzymana", usage="v!resume")
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.move_to(ctx.message.author.voice.channel)
        else:
            await Music.connect(self, ctx)
            vc = ctx.voice_client
        vc.resume()
        embed = discord.Embed(title="Wznowiono odtwarzanie muzyki", color=0x00AAFF)
        await ctx.send(embed=embed)

    @commands.command(aliases=['playqueue','musicqueue','vcqueue'], brief="Wyświetla kolejkę odtwarzania", description="Wyświetla 5 następnych piosenek do odtworzenia z kolejki", usage="v!queue")
    async def queue(self, ctx):
        try:
            if not playqueue or len(playqueue) < 1:
                title = "Brak piosenek w kolejce"
                description="Możesz dodać jakieś komendą v!play (link)"
            elif len(playqueue) <= 6 and len(playqueue) >=1:
                title = ("Aktualnie odtwarzane:\n"+playqueue[0]['title'])
                description = (str(len(playqueue)-1)+" piosenek do odtworzenia")
                for i in range(1, len(playqueue)):
                    if playqueue[i] is not None:
                        description = description + ("\n• "+playqueue[i]['title'])
                    else:
                        description = description + ("\n• ------------")
            else:
                title = ("Aktualnie odtwarzane:\n"+playqueue[0]['title'])
                description = (str(len(playqueue)-1)+" piosenek do odtworzenia")
                for i in range(1,6):
                    if playqueue[i] is not None:
                        description = description + ("\n• "+playqueue[i]['title'])
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

def setup(client):
    client.add_cog(Music(client))