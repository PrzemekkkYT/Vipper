import discord
from discord.channel import VoiceChannel
from discord.ext import commands
from datetime import date
import youtube_dl
import asyncio

intents= discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = "v!", intents=intents)

saveconvobool = 1
playqueue = []
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
YDL_OPTIONS = {'format':"bestaudio"}

@client.event
async def on_ready():
    print("Bot is ready")

@client.command()
async def test(ctx):
    await ctx.send("test")

#ilość aktywnych użytkowników i ich atrybuty w konsoli
@client.command()
async def active(ctx):
    amemb = ctx.guild.members
    amembcount = 0

    await ctx.send(len(amemb))
    await ctx.send("test")
    for memb in ctx.guild.members:
        print("==============")
        for attrib in dir(memb.activity):
            print(attrib)
        print("==============")

#aktywność danego użytkownika
@client.command()
async def act(ctx, member : discord.Member):
    for attrib in dir(member):
        print(attrib)
    print("================================================================")
    print(member.activities)
    print("================================================================")
    print(member.activity)
    print("================================================================")
    print(member.status)

#informacje o serwerze
@client.command()
async def serverinfo(ctx):
    svowner = ctx.guild.owner

    await ctx.send("owner:{}".format(svowner.name))
    await ctx.send("name:{}".format(ctx.guild.name))
    await ctx.send("members:{}".format(ctx.guild.member_count))
    await ctx.send("icon: {}".format(ctx.guild.icon_url))

#sprawdzenie informacji o właścicielu serwera
@client.command()
async def owtest(ctx):
    svowner = ctx.guild.owner

    owlist = dir(svowner)

    for attrib in owlist:
        print(attrib)

#napisanie kto jest właścicielem serwera
@client.command()
async def owner_find(ctx):
    guild_owner = client.get_user(int(ctx.guild.owner.id))
    await ctx.send(f'The owner of this server is: {guild_owner}')

#test wiadomości zawierającej embed
@client.command()
async def embedtest(ctx, title, desc, fdt, fdc):
    await ctx.send("embedtest")
    newembed = discord.Embed(title=title, description=desc, color=0x00FF33)
    newembed.add_field(name=fdt, value=fdc)
    await ctx.send(embed=newembed)

#informacje o serwerze w formie embed
@client.command()
async def serverinfoembed(ctx):
    infoembed = discord.Embed(title=("Nazwa: "+ctx.guild.name), color=0x00FFAA)
    infoembed.set_thumbnail(url=ctx.guild.icon_url)
    infoembed.set_author(name="Informacje o serwerze")
    infoembed.add_field(name="Właściciel:", value=ctx.guild.owner.name)
    infoembed.add_field(name="Ilość członków:", value=ctx.guild.member_count)
    infoembed.set_footer(text="Embed wygenerowany przez Vipper")
    await ctx.send(embed=infoembed)

#czy bot ma rejestrować wszystkie konwersacje na serwerze
@client.command()
async def saveconvo(ctx):
    global saveconvobool
    if saveconvobool > 0:
        saveconvobool = 0
        await ctx.send("Ta konwersacja nie będzie już rejestrowana")
    else:
        saveconvobool = 1
        await ctx.send("Rozpoczynam rejestrowanie konwersacji")

#rejestracja konwersacji do pliku tekstowego
@client.event
async def on_message(message):
    today = date.today()

    if saveconvobool > 0:
        guild = message.guild
        if guild:
            path = "chatlogs/{0}-{1}.txt".format(guild.id, today)  
            with open(path, 'a+', encoding="utf-8") as f:
                if len(message.attachments) > 0:
                    print("{0.id} | {0.created_at} | {0.channel.name}({0.channel.id}) | {0.author} | {0.content} | att: {0.attachments[0].url}".format(message), file=f)
                else:
                    print("{0.id} | {0.created_at} | {0.channel.name}({0.channel.id}) | {0.author} | {0.content}".format(message), file=f)
    await client.process_commands(message)

#rejestracja do pliku tekstowego czy edytowano wiadomość
@client.event
async def on_message_edit(before, after):
    today = date.today()

    if saveconvobool > 0:
        guild = after.guild
        if guild:
            path = "chatlogs/{0}-{1}.txt".format(guild.id, today)  
            with open(path, 'a+', encoding="utf-8") as f:
                if len(after.attachments) > 0:
                    print("EDITED: {0.id} | {0.created_at} | {0.channel.name}({0.channel.id}) | {0.author} | BEFORE: {1.content} | AFTER: {0.content} | att: {0.attachments[0].url}".format(after, before), file=f)
                else:
                    print("EDITED: {0.id} | {0.created_at} | {0.channel.name}({0.channel.id}) | {0.author} | BEFORE: {1.content} | AFTER: {0.content}".format(after, before), file=f)

#rejestracja do pliku tekstowego czy usunięto wiadomość
@client.event
async def on_message_delete(message):
    today = date.today()

    if saveconvobool > 0:
        guild = message.guild
        if guild:
            path = "chatlogs/{0}-{1}.txt".format(guild.id, today)  
            with open(path, 'a+', encoding="utf-8") as f:
                if len(message.attachments) > 0:
                    print("DELETED: {0.id} | {0.created_at} | {0.channel.name}({0.channel.id}) | {0.author} | {0.content} | att: {0.attachments[0].url}".format(message), file=f)
                else:
                    print("DELETED: {0.id} | {0.created_at} | {0.channel.name}({0.channel.id}) | {0.author} | {0.content}".format(message), file=f)

@client.command()
async def sendembed(ctx, color : int, *, title):
    embed = discord.Embed(title=title, color=color)
    await ctx.send(embed=embed)

@client.command()
async def connect(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send("Połączono z kanałem głosowym "+channel.name)
    else:
        await ctx.send("Użytkownik nie jest połączony z żadnym kanałem głosowym")

@client.command()
async def leave(ctx):
    if (ctx.voice_client):
        await ctx.send("Opuszczono kanał głosowy")
        await ctx.guild.voice_client.disconnect()
    else:
        await ctx.send("Bot nie jest połączony z żadnym kanałem głosowym")

def song_search(src):
    with youtube_dl.YoutubeDL(YDL_OPTIONS ) as ydl:
        info = ydl.extract_info(f"ytsearch:{src}", download=False)['entries'][0]
        
    return {'source': info['formats'][0]['url'], 'title': info['title']}

def play_next(ctx):
    vc = ctx.voice_client
    if len(playqueue) > 1:
        del playqueue[0]
        vc.play(discord.FFmpegPCMAudio(playqueue[0]['source'], **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
        vc.is_playing()

@client.command()
async def play(ctx, url : str):
    vc = ctx.voice_client
    song = song_search(url)
    playqueue.append(song)

    if vc:
        await vc.move_to(ctx.message.author.voice.channel)
    else:
        await connect(ctx)
        vc = ctx.voice_client

    if not vc.is_playing():
        vc.play(discord.FFmpegPCMAudio(playqueue[0]['source'], **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
        vc.is_playing()
    else:
        queueembed = discord.Embed(title=("Dodano \""+playqueue[-1]['title']+"\" do kolejki"), color=0x00AAFF)
        await ctx.send(embed=queueembed)
        

client.run('TOKEN')
