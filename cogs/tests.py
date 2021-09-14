import discord
import sqlite3, traceback, json, os, requests
from discord.ext import commands
from discord.ext.commands.core import command
from discord.message import Attachment
from discord_components import *
from discord.abc import Messageable
from datetime import date, datetime

class Tests(commands.Cog):
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
    #cmds_categories = []

    @commands.Cog.listener()
    async def on_ready(self):
        DiscordComponents(self.client)
        for command in self.client.commands:
            self.cmds.append(command)
        #for i in range(len(self.cmds)):
        #    if self.cmds[i].cog_name not in self.cmds_categories:
        #        self.cmds_categories.append(self.cmds[i].cog_name)
        #    else: pass

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
                if self.cmds[j].cog_name == self.cmds_categories[i]:
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
        message_ca = ctx.message.created_at.replace(hour=(ctx.message.created_at.hour+2))
    
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
        message_ca = ctx.message.created_at.replace(hour=(ctx.message.created_at.hour+2))
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
                await ctx.send(rj["freeGames"]["current"][-i]["price"]["totalPrice"]["fmtPrice"]["discountPrice"]+": "+rj["freeGames"]["current"][-i]["price"]["totalPrice"]["fmtPrice"]["discountPrice"+"zł"])

def setup(client):
    client.add_cog(Tests(client))