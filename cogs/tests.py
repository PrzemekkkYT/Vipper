import math
import random
from typing import Match

from deep_translator import GoogleTranslator
from cogs.music import Music, FFMPEG_OPTIONS
import discord
import sqlite3, json, os, requests, io, useful, threading, asyncio
from discord import integrations
from gtts.tts import gTTS
from discord.utils import find
from discord.mentions import AllowedMentions
from discord.ext import commands
from discord.ext.commands.core import command
from discord.message import Attachment
from discord_components import *
from discord.abc import Messageable
from datetime import date, datetime, timedelta
from gtts import gTTS
from useful import fixConfig, translate, fixPolls, morse
# from textblob import TextBlob
import langid

class Tests(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, client):
        self.client = client

    fg_request_url = "https://free-epic-games.p.rapidapi.com/free"

    fg_request_headers = {
        'x-rapidapi-host': "free-epic-games.p.rapidapi.com",
        'x-rapidapi-key': "4a35b378bemsh2dad8e6bec18de1p119880jsne3276f501ab7"
    }

    fg_response = requests.request("GET", fg_request_url, headers=fg_request_headers)

    con = sqlite3.connect('tests.db')
    cursor = con.cursor()

    cmds = []
    cmds_names = []
    cmds_categories = []

    @commands.Cog.listener()
    async def on_ready(self):
        DiscordComponents(self.client)
        for command in self.client.commands:
            self.cmds.append(command)
        for i in range(len(self.cmds)):
            if self.cmds[i].cog_name not in self.cmds_categories:
                self.cmds_categories.append(self.cmds[i].cog_name)
            else: pass
        for i in range(len(self.cmds)):
            if self.cmds[i].name not in self.cmds_names:
                self.cmds_names.append(self.cmds[i].name)
            else: pass
        self.checkTime()
        
    @commands.command()
    async def buttonstest(self, ctx):

        m = await ctx.send("sadiugfasdas",
            components=[[Button(style=1, label="Test")]]
        )

        res = await self.client.wait_for("button_click")
        if res.channel == ctx.message.channel:
            await m.edit("test")

    @commands.command()
    async def testhelp(self, ctx):
        embed = discord.Embed(title="Komendy bota Vipper:", color=0x55FF55)
        embed.add_field(name="Kategoria1", value="komenda1, komenda2, komenda3, komenda4", inline=False)
        embed.add_field(name="Kategoria2", value="komenda1, komenda2, komenda3, komenda4", inline=False)
        embed.add_field(name="Kategoria3", value="komenda1, komenda2, komenda3, komenda4", inline=False)
        embed.add_field(name="Kategoria4", value="komenda1, komenda2, komenda3, komenda4", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def testhelpauto(self, ctx):
        embed = discord.Embed(title="Komendy bota Vipper:",color=0x55FF55)
        categories = []
        for i in range(len(self.cmds_categories)):
            temp2 = {}
            temp3 = []
            for j in range(len(self.cmds)):
                if self.cmds[j].cog_name == self.cmds_categories[i] and self.cmds[j].hidden != True:
                    temp3.append(self.cmds[j].name)
                temp2 = {'category': self.cmds_categories[i], 'cmds': temp3}
            categories.append(temp2)
        for i in range(len(self.cmds_categories)):
            if self.cmds_categories[i] is not None:
                embed.add_field(name=categories[i]['category'], value=(", ".join(categories[i]['cmds'])), inline=False)
            else: embed.add_field(name="Nieskategoryzowane", value=(", ".join(categories[i]['cmds'])), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def hasembed(self, ctx, id: int):
        message = await ctx.channel.fetch_message(id)
        print("EMBED: title: {0.title} | author: {0.author} | description: {0.description} | color: {0.color} | fields: {0.fields} | footer: {0.footer} | image: {0.image} | provider: {0.provider} | thumbnail: {0.thumbnail} | timestamp: {0.timestamp} | type: {0.type} | url: {0.url} | video: {0.video}".format(message.embeds[0]))

    @commands.command()
    async def mca(self, ctx):
        message = ctx.message
        print("today: "+str(message.created_at))
        print("today: "+str(message.created_at.replace(hour=(message.created_at.hour+2))))

    @commands.command()
    async def fgembed(self, ctx, chid, shop, fu, url, *, title):
        freeuntil = fu.split("-")
        channel = self.client.get_channel(int(chid))
        embed = discord.Embed(title=title, url=url)
        embed.add_field(name="Darmowe do", value=(freeuntil[0]+"."+freeuntil[1]+"."+freeuntil[2]))
        if shop=="epicgames":
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/d/d0/Epic_games_store_logo.png")
        elif shop=="steam":
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/2048px-Steam_icon_logo.svg.png")
        elif shop=="ubisoft":
            embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/7/78/Ubisoft_logo.svg")
        await channel.send(embed=embed)

    @commands.command()
    async def database(self, ctx):
        today = date.today()
        message_ca = self.utc_to_local(ctx.message.created_at.utcnow())
    
        self.cursor.execute("create table if not exists '{0}-{1.month}-{1.year}' (db_id int, message_id int, message_ca text, channel_name text, channel_id int, author text, content text, att text)".format(ctx.guild.id, today))

        self.cursor.execute("select max(db_id) from '{0}-{1.month}-{1.year}'".format(ctx.guild.id, today))
        db_id = self.cursor.fetchone()[0]
        if db_id is None:
            db_id = 0
            self.cursor.execute("insert into '{0}-{1.month}-{1.year}' values (0, 0, '0', '0', 0, '0', '0', '0')".format(ctx.guild.id, today))

        if len(ctx.message.attachments) > 0:
            self.cursor.execute("insert into '{0}-{1.month}-{1.year}' values ({2}, {3.id}, '{4}', '{3.channel.name}', {3.channel.id}, '{3.author}', '{3.content}', '{3.attachments[0]}')".format(ctx.guild.id, today, db_id+1, ctx.message, message_ca))
        else:
            self.cursor.execute("insert into '{0}-{1.month}-{1.year}' values ({2}, {3.id}, '{4}', '{3.channel.name}', {3.channel.id}, '{3.author}', '{3.content}', 'No Attachments')".format(ctx.guild.id, today, db_id+1, ctx.message, message_ca))

        #self.cursor.execute("select max(db_id) from september")
        #db_id = self.cursor.fetchone()
        #print(db_id[0])
        #self.cursor.execute("insert into september values ({0}, {1}, {2})".format(db_id[0]+1, ctx.channel.id, ctx.message.id))
        #self.cursor.execute("select * from september")
        #print(self.cursor.fetchall())
        self.con.commit()

    @commands.command()
    async def jsonsave(self, ctx):
        today = date.today()
        message_ca = self.utc_to_local(ctx.message.created_at.utcnow())
        path = "logs/chat/{0}-{1}.json".format(ctx.guild.id, today)

        attachments = []
        for attachment in ctx.message.attachments:
            attachments.append({
                "id":attachment.id,
                "filename":attachment.filename,
                "url":attachment.url,
                "content_type":attachment.content_type,
                "height":attachment.height,
                "width":attachment.width,
                "size":attachment.size,
                "proxy_url":attachment.proxy_url
            })
        message_info = {
            "message_id":ctx.message.id,
            "message_ca":str(message_ca),
            "channel_name":ctx.message.channel.name,
            "channel_id":ctx.message.channel.id,
            "author":str(ctx.message.author),
            "content":ctx.message.content,
            "attachments":attachments
        }
        if not os.path.exists(path) or os.path.getsize(path)<=0:
            with open(path, 'a') as json_file: json.dump({"logs":[]}, json_file, indent=4)
        with open(path, 'r+') as json_file:
            file_data = json.load(json_file)
            file_data["logs"].append(message_info)
            json_file.seek(0)
            json.dump(file_data, json_file, indent=4)
    
    @commands.command()
    async def setfg(self, ctx, channel:int):
        text_channel = ctx.guild.get_channel(channel)
        self.cursor.execute("create table if not exists free_games_channel (guild_id int not null unique, channel_id int not null unique)")
        self.cursor.execute(f"insert into free_games_channel (guild_id, channel_id) values({ctx.guild.id}, {text_channel.id}) on conflict(guild_id) do update set channel_id={text_channel.id}")
        await ctx.send(f"Od teraz na kanale {text_channel.name} będą wysyłane informacje o darmowych grach")
        self.con.commit()

    @commands.command()
    async def postfg(self, ctx, name):
        self.cursor.execute("select * from free_games_channel")
        guilds_ids = self.cursor.fetchall()
        for gid in guilds_ids:
            print(gid[0])
            guild = self.client.get_guild(gid[0])
            channel = guild.get_channel(gid[1])
            await channel.send(name)

    @commands.command()
    async def getfg(self, ctx):
        rj = self.fg_response.json()

        for i in range(len(rj["freeGames"]["current"])):
            if rj["freeGames"]["current"][-i]["promotions"] and rj["freeGames"]["current"][-i]["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["discountSetting"]["discountPercentage"] == 0:
                await ctx.send(rj["freeGames"]["current"][-i]["title"]+": "+rj["freeGames"]["current"][-i]["price"]["totalPrice"]["fmtPrice"]["discountPrice"])

    @commands.command()
    async def sendfile(self, ctx, udate):
        path_chat = 'logs/chat/C-{0}-{1}.json'.format(ctx.guild.id, udate)
        print("==============================================================="+path_chat)
        with open(path_chat, "rb") as f:
            data = io.BytesIO(f.read())
            await ctx.send(file=discord.File(data, filename=path_chat[9:]))

    @commands.command()
    async def currentfg(self, ctx : commands.Context):
        rj = self.fg_response.json()
        current = []
        for i in range(len(rj["freeGames"]["current"])):
            if rj["freeGames"]["current"][-i]["promotions"] and rj["freeGames"]["current"][-i]["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["discountSetting"]["discountPercentage"] == 0:
                current.append(rj["freeGames"]["current"][-i])

        for fg in current:
            free_until = fg["price"]["lineOffers"][0]["appliedRules"][0]["endDate"]
            embed = discord.Embed(title=fg["title"], url=("https://www.epicgames.com/store/pl/p/"+fg["title"].replace(" ", "-").lower()))
            embed.set_author(name="Darmowa giera tygodnia:", icon_url=self.client.user.avatar_url)
            embed.add_field(name="Darmowa od", value=useful.better_date(fg["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["startDate"]), inline=False)
            embed.add_field(name="Darmowa do", value=useful.better_date(free_until), inline=False)
            embed.set_thumbnail(url="https://cdn2.pu.nl/media/sven/epicgameslogo.png")

            for image in fg["keyImages"]:
                if image["type"] == "OfferImageWide":
                    embed.set_image(url=image["url"].replace(" ","%20"))

            embed.set_footer(text="Kliknij na nazwę aby przejść do sklepu")
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)
    
    @commands.command()
    async def buttonscalc(self, ctx):
        m = await ctx.send("sadiugfasdas",
            components=[
                [Button(style=1, label="7"),Button(style=1, label="8"),Button(style=1, label="9"),Button(style=1, label="X")],
                [Button(style=1, label="4"),Button(style=1, label="5"),Button(style=1, label="6"),Button(style=1, label="-")],
                [Button(style=1, label="1"),Button(style=1, label="2"),Button(style=1, label="3"),Button(style=1, label="+")],
                [Button(style=1, label="00"),Button(style=1, label="0"),Button(style=1, label=","),Button(style=1, label="=")]
            ]
        )

        while m.created_at < (datetime.utcnow() + timedelta(minutes=5)):
            res = await self.client.wait_for("button_click")
            if res.channel == ctx.message.channel:
                #for attrib in dir(res.responded):
                #    print(attrib)
                await m.edit(res.component.label)

    @commands.command()
    async def auditlog(self, ctx):
        entries = await ctx.guild.audit_logs(limit=None, user=ctx.guild.owner).flatten()
        for entry in entries:
            with open("entries.txt", "a+") as f:
                f.write(str(entry)+"\n")

    def checkTime(self):
        t1 = threading.Timer(1, self.checkTime)
        t1.daemon = True
        t1.start()
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        if current_time=="16:52:20":
            print("16:52:20")

    @commands.command()
    async def testcfg(self, ctx):
        embed = discord.Embed(title="test")
        embed.set_image(url="https://cdn1.epicgames.com/epic/offer/TheEscapists_Newsfeed Post-2560x1440-587a8d844cab1246b3253f2f98fab8a7.jpg".replace(" ","%20"))
        await ctx.send(embed=embed)

        rj = self.fg_response.json()
        crnt = rj["freeGames"]["current"][0]
        for image in crnt["keyImages"]:
            if image["type"] == "OfferImageWide":
                print(image["url"])

    @commands.command()
    async def findvc(self, ctx):
        vcs = []
        for guild in self.client.guilds:
            print("guild.id:",guild.id)
            vcs.append(find(lambda v: len(v.members)>0, guild.voice_channels))
        for vc in vcs:
            if vc:
                await vc.connect()
                print("połączono z",vc.guild.id)
                await Music.play(self, ctx, "https://www.youtube.com/watch?v=_o9mZ_DVTKA")
            else: print("brak użytkowników na kanałach głosowych")
        
    @commands.command()
    async def queuelen(self, ctx):
        from cogs.music import playcontext
        if playcontext:
            if self.client.voice_clients:
                song = Music.song_search(Music, "https://www.youtube.com/watch?v=_o9mZ_DVTKA")
                for voiceclient in self.client.voice_clients:
                    if voiceclient.is_playing():
                        voiceclient.stop()
                        voiceclient.play(discord.FFmpegPCMAudio(song['source'], **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(Music.play_next(Music, voiceclient, playcontext[voiceclient.guild.id]), voiceclient.loop))
                    else:
                        voiceclient.play(discord.FFmpegPCMAudio(song['source'], **FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(Music.play_next(Music, voiceclient, playcontext[voiceclient.guild.id]), voiceclient.loop))

    @commands.command()
    async def getallmembers(self, ctx):
        with open("members.txt", "a+", encoding="utf-8") as f:
            for member in ctx.guild.members:
                f.write(f"{member.name}: {member.id}\n")
        
    @commands.command()
    async def waitfortest(self, ctx):
        await ctx.send("Dodaj dowolną reakcję")
        reaction, user = await ctx.bot.wait_for('reaction_add')
        await ctx.send(f"{user} zareagował {reaction}")
        
    @commands.command()
    async def printweekday(self, ctx):
        print(datetime.today().weekday())
        
    @commands.command()
    async def emoji(self, ctx, emoji):
        emoji = self.client.get_emoji(emoji)
        print(emoji)
        await ctx.send(emoji)
        
    @commands.command()
    async def ttstest(self, ctx, *, text):
        sound = gTTS(text=text, lang="pl")
        sound.save("tts.mp3")
        ctx.voice_client.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/ffmpeg.exe", source="E:/DiscordBot/PyVipper/tts.mp3"))
        
    @commands.command()
    async def langtest(self, ctx, *, text):
        await ctx.send(translate(ctx.guild.id, text))
        
    @commands.command()
    async def procents(self, ctx, msgid, first, second):
        #await ctx.send(f"{first} w {second} = {(float(first)/float(second))*100}%")
        first, second = float(first),float(second)
        full = first+second
        # await ctx.send(f"{full}, {'%.2f'%((first/full)*100)}%, {'%.2f'%((second/full)*100)}%")
        msg = await ctx.fetch_message(msgid)
        embed = discord.Embed(title=f"{'%.2f'%((first/full)*100)}% | {'%.2f'%((second/full)*100)}%")
        await msg.edit(embed=embed)
        
    @commands.command()
    async def editembed(self, ctx, msgid):
        msg = await ctx.fetch_message(msgid)
        print(msg)
        newembed = discord.Embed(title="test123")
        await msg.edit(embed=newembed)
        print(msg.embeds[0].title)
        
    @commands.command()
    async def probuttons(self, ctx):
        await ctx.send(
            "Buttons!",
            components=[
                [Button(label="Button1", custom_id="button1"),
                Button(label="Button2", custom_id="button2")]
            ]
        )
        
    @commands.command()
    async def whatsplaying(self, ctx, id):
        await ctx.send(f"Desktop Status: {ctx.guild.get_member(int(id)).desktop_status}")
        await ctx.send(f"Status: {ctx.guild.get_member(int(id)).status}")
        #await ctx.send(f"Activity: {ctx.guild.get_member(int(id)).activity}")
        activity = ctx.guild.get_member(int(id)).activity
        print(type(activity))
        print(activity.type)
        print(activity.name)
        print(activity.details)

    @commands.command()
    async def userbyid(self, ctx, id):
        await ctx.send(f"Użytkownik z ID: 397068546154299404 to: {ctx.guild.get_member(int(id)).name}")

    @commands.command()
    async def timetest(self, ctx):
        print(datetime.now() < (datetime.now()-timedelta(minutes=1)))

    @commands.command()
    async def pastebin(self, ctx, url):
        print(requests.get(url).text)

    @commands.command()
    async def translatemixer(self, ctx, times, *, text):
        langs = ['af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg', 'ca', 'ceb', 'ny', 'co', 'hr', 'cs', 'da', 'nl', 'en', 'eo', 'et', 'tl', 'fi', 'fr', 'fy', 'gl', 'ka', 'de', 'el', 'gu', 'ht', 'ha', 'haw', 'iw', 'hi', 'hmn', 'hu', 'is', 'ig', 'id', 'ga', 'it', 'ja', 'jw', 'kn', 'kk', 'km', 'ko', 'ku', 'ky', 'lo', 'la', 'lv', 'lt', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'my', 'ne', 'no', 'ps', 'fa', 'pl', 'pt', 'pa', 'ro', 'ru', 'sm', 'gd', 'sr', 'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es', 'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'uz', 'vi', 'cy', 'xh', 'yi', 'yo', 'zu', 'fil', 'he']
        print("translatemixer")
        # lang = TextBlob(text).detect_language()
        lang = langid.classify(text)
        for i in range(int(times)):
            rnglang = random.choice(langs)
            text = GoogleTranslator(target=rnglang).translate(text)
            await ctx.send(f"{rnglang}: {text}")
        text = GoogleTranslator(target=lang[0]).translate(text)
        await ctx.send(f"{lang[0]}: {text}")

    @commands.command()
    async def rolecolor(self, ctx, role_id):
        role = ctx.guild.get_role(int(role_id))
        await ctx.send(f"value: {role.color.value}, r: {role.color.r}, g: {role.color.g}, b: {role.color.b}")
        
        
def setup(client):
    client.add_cog(Tests(client))