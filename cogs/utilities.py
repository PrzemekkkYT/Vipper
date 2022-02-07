import discord
from discord.mentions import AllowedMentions
from discord.ext import commands
from discord.utils import find
from discord_components import *
import traceback, useful, requests, sqlite3, io
from datetime import date, datetime
from PIL import Image
from pytesseract import pytesseract
import json
from useful import translate, fixConfig, fixPolls

pytesseract.tesseract_cmd = r"E:\Tesseract-OCR\tesseract"

class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    cmds = []
    cmds_names = []
    cmds_categories = []
    
    #temp
    cogs = {}
    cogs['uncategorized'] = []

    fg_request_url = "https://free-epic-games.p.rapidapi.com/free"
    fg_request_headers = {
        'x-rapidapi-host': "free-epic-games.p.rapidapi.com",
        'x-rapidapi-key': "4a35b378bemsh2dad8e6bec18de1p119880jsne3276f501ab7"
    }
    fg_response = requests.request("GET", fg_request_url, headers=fg_request_headers)

    con = sqlite3.connect('tests.db')
    cursor = con.cursor()

    @commands.Cog.listener()
    async def on_ready(self):
        #temp
        for cog in self.client.cogs:
            self.cogs[cog] = []
        for command in self.client.commands:
            if command.hidden != True:
                if command.cog_name is not None:
                    self.cogs[command.cog_name].append(command.name)
                else: self.cogs['uncategorized'].append(command.name)
        #print(self.cogs)
        self.cogs = {k: v for k, v in self.cogs.items() if v}
            
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

    @commands.command(brief="help.brief", description="help.description", usage="help.usage")
    async def help(self, ctx, selection=None):
        try:
            selected = find(lambda s: s.name == selection, self.cmds)
            if selection is not None and selected is None:
                selected = find(lambda s: any(alias == selection for alias in s.aliases) == True, self.cmds)
            selection_c = str(selection).capitalize()

            if selection is None:
                embed = discord.Embed(title=translate(ctx.guild.id, "help.title"), color=0x55FF55)
                    
                for cog, commands in self.cogs.items():
                    if cog != "uncategorized": embed.add_field(name=cog, value=(", ".join(commands)), inline=False)
                    else: embed.add_field(name=translate(ctx.guild.id, "help.uncategorized"), value=(", ".join(commands)), inline=False)
                
                embed.set_footer(text=translate(ctx.guild.id, "help.footer"))
                await ctx.send(embed=embed)
            elif selection_c in self.cogs: #self.cmds_categories
                embed = discord.Embed(title=(translate(ctx.guild.id, "help.category")+": "+selection_c), color=0x55FF55)
                for i in range(len(self.cmds)):
                    if self.cmds[i].cog_name == selection_c:
                        embed.add_field(name=self.cmds[i].name, value=translate(ctx.guild.id, self.cmds[i].brief), inline=False)
                await ctx.send(embed=embed)
            elif selection in self.cmds_names or selected:
                embed = discord.Embed(title=(translate(ctx.guild.id, "help.command", [selected.name])), color=0x55FF55)
                if selected.cog_name:
                    embed.add_field(name=translate(ctx.guild.id, "help.category"), value=selected.cog_name, inline=False)
                else: embed.add_field(name=translate(ctx.guild.id, "help.category"), value=translate(ctx.guild.id, "help.nocategory"), inline=False)
                if selected.aliases:
                    embed.add_field(name=translate(ctx.guild.id, "help.aliases"), value=(', '.join(selected.aliases)))
                else: embed.add_field(name=translate(ctx.guild.id, "help.aliases"), value=translate(ctx.guild.id, "help.noaliases"), inline=False)
                if selected.description:
                    embed.add_field(name=translate(ctx.guild.id, "help.desc"), value=translate(ctx.guild.id, selected.description), inline=False)
                else: embed.add_field(name=translate(ctx.guild.id, "help.desc"), value=translate(ctx.guild.id, "help.nodesc"), inline=False)
                if selected.usage:
                    embed.add_field(name=translate(ctx.guild.id, "help.syntax"), value=translate(ctx.guild.id, selected.usage), inline=False)
                else: embed.add_field(name=translate(ctx.guild.id, "help.syntax"), value=translate(ctx.guild.id, "help.nosyntax"), inline=False)
                await ctx.send(embed=embed)
        except Exception as inst:
            embed = discord.Embed(title=translate(ctx.guild.id, "help.cmdnofound"), color=0x55FF55)
            await ctx.send(embed=embed)
            print("===========! HELP TRACEBACK !===========")
            traceback.print_tb(inst.__traceback__)
            print("================! INST !================")
            print(inst)
            print("===========! HELP TRACEBACK !===========")

    async def postcurrentfg(self, client):
        print("1")
        self.fg_response = requests.get(self.fg_request_url, headers=self.fg_request_headers)
        rj = self.fg_response.json()
        current = []
        print("2")
        for i in range(len(rj["freeGames"]["current"])):
            if rj["freeGames"]["current"][-i]["promotions"] and rj["freeGames"]["current"][-i]["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["discountSetting"]["discountPercentage"] == 0:
                current.append(rj["freeGames"]["current"][-i])
        print("3")
        for fg in current:
            print("3.5")
            try:
                free_until = fg["price"]["lineOffers"][0]["appliedRules"][0]["endDate"]
            except:
                free_until = fg["expiryDate"]
            print("4")
            title = fg["title"]
            specialChars = "!#$%^&*()" 
            for specialChar in specialChars:
                print("5")
                title = title.replace(specialChar, "")
            embed = discord.Embed(title=fg["title"], url=("https://www.epicgames.com/store/pl/p/"+title.replace(" ", "-").lower()))
            embed.set_author(name="Darmowa giera tygodnia:", icon_url=client.user.avatar_url)
            embed.add_field(name="Darmowa od", value=useful.better_date(fg["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["startDate"]), inline=False)
            embed.add_field(name="Darmowa do", value=useful.better_date(free_until), inline=False)
            embed.set_thumbnail(url="https://cdn2.pu.nl/media/sven/epicgameslogo.png")
            print("6")
            for image in fg["keyImages"]:
                if image["type"] == "OfferImageWide":
                    embed.set_image(url=image["url"].replace(" ","%20"))
            print("7")
            embed.set_footer(text="Kliknij na nazwę aby przejść do sklepu")
            embed.timestamp = datetime.utcnow()
            print("8")
            self.cursor.execute("select * from free_games_channel")
            guilds_ids = self.cursor.fetchall()
            for gid in guilds_ids:
                print(gid[0])
                guild = client.get_guild(gid[0])
                channel = guild.get_channel(gid[1])
                await channel.send(content="@everyone", embed=embed, allowed_mentions=AllowedMentions(everyone=True))

    @commands.command(brief="ocr.brief", description="ocr.description", usage="ocr.usage")
    async def ocr(self, ctx, url):
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        embed = discord.Embed(title="Tekst z obrazu", description=f"```{pytesseract.image_to_string(img, lang='pol')}```")
        embed.set_thumbnail(url=url)
        await ctx.send(embed=embed)
        
    @commands.command(brief="setlang.brief", description="setlang.description", usage="setlang.usage")
    async def setlang(self, ctx, lang=None):
        guild_id = str(ctx.guild.id)
        fixConfig(guild_id)
        if lang=="langs":
            langs = ""
            for lng in json.load(open("langs.json", "r", encoding="utf-8")):
                langs += lng+", "
            await ctx.send(translate(ctx.guild.id, "setlang.langlist", [langs]))
        elif lang is not None:
            if lang in json.load(open("langs.json", "r", encoding="utf-8")):
                with open("config.json", 'r+', encoding="utf-8") as json_file:
                    file_data = json.load(json_file)
                    if lang != file_data["configs"][guild_id]["lang"]:
                        file_data["configs"][guild_id]["lang"] = lang
                        json_file.seek(0)
                        json.dump(file_data, json_file, indent=4, ensure_ascii=False)
                        await ctx.send(translate(ctx.guild.id, "setlang.langset", [lang]))
                    else: await ctx.send(translate(ctx.guild.id, "setlang.alreadyset", [lang]))
            else: await ctx.send(translate(ctx.guild.id, "setlang.nolang", [lang]))
        else: await ctx.send(translate(ctx.guild.id, "setlang.current", [json.load(open("config.json", 'r+', encoding="utf-8"))["configs"][str(ctx.guild.id)]["lang"]]))
    
    @commands.command(brief="initpoll.brief", description="initpoll.description", usage="initpoll.usage")
    async def initpollold(self, ctx, *, options):
        options = options.split(" | ")
        name = options.pop(0)
        print(options)
        components = []
        if 1 < len(options) <= 5:
            for option in options:
                components.append(Button(label=option, custom_id=option))
        else:
            await ctx.send("Minimalnie 2 i maksymalnie 5 możliwości!")
            return
        
        embed = discord.Embed(title=name, description="Wszystkie głosy: 0")
        for option in options:
            embed.add_field(name=(option+" 0.00%"), value=("░"*20), inline=False)
        msg = await ctx.send(embed=embed, components=[components])
        #self.polls[msg.id] = {}
        guild_id = str(ctx.guild.id)
        msg_id = str(msg.id)
        fixPolls(guild_id)
        with open("polls.json", "r+", encoding="utf-8") as file:
            file_data = json.load(file)
            if msg_id not in file_data[guild_id]: file_data[guild_id][msg_id] = {}
            if "title" not in file_data[guild_id][msg_id]: file_data[guild_id][msg_id]["title"] = name
            if "options" not in file_data[guild_id][msg_id]: file_data[guild_id][msg_id]["options"] = {}
            if "voters" not in file_data[guild_id][msg_id]: file_data[guild_id][msg_id]["voters"] = {}
            for option in options:
                file_data[guild_id][msg_id]["options"][option] = 0
            file.seek(0)
            json.dump(file_data, file, indent=4, ensure_ascii=False)
            file.close()
    
    def is_dev(ctx):
        return ctx.message.author.id == 183242057882664961
    
    @commands.command(hidden=True)
    @commands.check(is_dev)
    async def manualfreegames(self, ctx, fgurl=""):
        if fgurl=="":
            await ctx.send("Nie podano linku do pastebin zawierającego kod json darmówki!")
            return
        self.cursor.execute("select * from free_games_channel")
        guilds_ids = self.cursor.fetchall()
        file_data = json.loads(requests.get(fgurl).text)
        for game in file_data:
            embed = discord.Embed(title=game["title"], url=game["url"])
            if game["comment"] is None or game["comment"] == "":
                embed.set_author(name="Darmowa giera tygodnia:", icon_url=self.client.user.avatar_url)
            else: embed.set_author(name=game["comment"], icon_url=self.client.user.avatar_url)
            
            try: embed.add_field(name="Darmowa od", value=useful.better_date(game["start-date"]), inline=False)
            except: embed.add_field(name="Darmowa od", value=game["start-date"], inline=False)
            
            try: embed.add_field(name="Darmowa do", value=useful.better_date(game["end-date"]), inline=False)
            except: embed.add_field(name="Darmowa do", value=game["end-date"], inline=False)
            
            try:
                if game["shop"] == "epicgames": embed.set_thumbnail(url="https://cdn2.pu.nl/media/sven/epicgameslogo.png")
                elif game["shop"] == "steam": embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/2048px-Steam_icon_logo.svg.png")
                elif game["shop"] == "ubisoft": embed.set_thumbnail(url="https://www.pngkit.com/png/full/40-407342_2018-ubisoft-entertainment-ubisoft-logo-2017-png.png")
            except:
                embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/No-Symbol.svg/768px-No-Symbol.svg.png")
            
            embed.set_image(url=game["img-url"])
            embed.set_footer(text="Kliknij na nazwę aby przejść do sklepu")
            embed.timestamp = datetime.utcnow()
            
            for gid in guilds_ids:
                print(f"Posted free game on guild: {gid[0]}")
                guild = self.client.get_guild(gid[0])
                channel = guild.get_channel(gid[1])
                await channel.send(content="@everyone", embed=embed, allowed_mentions=AllowedMentions(everyone=True))
    
def setup(client):
    client.add_cog(Utilities(client))