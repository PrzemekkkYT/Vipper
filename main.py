from inspect import Traceback
import discord
from discord.ext import commands, tasks
from datetime import datetime, timezone
import os, json

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = "v!", intents=intents)
client.remove_command("help")

initial_extensions = ['cogs.music']

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

config_file = open("config.json", "r")
config = json.load(config_file)

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="dlaczego Tede kurwą jest"))
    presenceLoop.start()
    #await client.change_presence(status=discord.Status.idle, activity=discord.Game("dlaczego Tede kurwą jest"))
    print("Bot is ready")

@tasks.loop(seconds=5) 
async def presenceLoop():
    vcs = []
    membs = 0
    for guild in client.guilds:
        if guild.voice_client:
            vcs.append(guild.voice_client)
    if len(vcs) >= 1:
        for vc in vcs:
            membs += len(vc.channel.members)-1
        await client.change_presence(status=discord.Status.idle, activity=discord.Game(name=f"{membs} słucha na {len(vcs)} serwerach"))
    else: await client.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="dlaczego Tede kurwą jest"))

@client.command()
async def test(ctx):
    await ctx.send("test")

#ilość aktywnych użytkowników i ich atrybuty w konsoli
@client.command(hidden=True)
async def active(ctx):
    amemb = ctx.guild.members

    await ctx.send(len(amemb))
    await ctx.send("test")
    for memb in ctx.guild.members:
        print("==============")
        for attrib in dir(memb.activity):
            print(attrib)
        print("==============")

#aktywność danego użytkownika
@client.command(hidden=True)
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
@client.command(hidden=True)
async def serverinfo(ctx):
    svowner = ctx.guild.owner

    await ctx.send("owner:{}".format(svowner.name))
    await ctx.send("name:{}".format(ctx.guild.name))
    await ctx.send("members:{}".format(ctx.guild.member_count))
    await ctx.send("icon: {}".format(ctx.guild.icon_url))

#sprawdzenie informacji o właścicielu serwera
@client.command(hidden=True)
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
@client.command(hidden=True)
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

@client.command(hidden=True)
async def sendembed(ctx, color : int, *, title):
    embed = discord.Embed(title=title, color=color)
    await ctx.send(embed=embed)

client.run(config["token"])