import discord
from discord.mentions import AllowedMentions
from discord.ext import commands
from discord.utils import find
import traceback, useful, requests, sqlite3, io
from datetime import date, datetime
from PIL import Image
from pytesseract import pytesseract
import json
from useful import translate, fixConfig

pytesseract.tesseract_cmd = r"E:\Tesseract-OCR\tesseract"

class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    cmds = []
    cmds_names = []
    cmds_categories = []

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
            #print("name: "+selected.name) if selected.name else print("name: None")
            #print("help: "+selected.help) if selected.help else print("help: None")
            #print("brief: "+selected.brief) if selected.brief else print("brief: None")
            #print("usage: "+selected.usage) if selected.usage else print("usage: None")
            #print("aliases: "+selected.aliases) if selected.aliases else print("aliases: None")
            #print("desc: "+selected.description) if selected.description else print("desc: None")
            #print("full_parent_name: "+selected.full_parent_name) if selected.full_parent_name else print("full_parent_name: None")
            #print("qualified_name: "+selected.qualified_name) if selected.qualified_name else print("qualified_name: None")
            #print("cog_name: "+selected.cog_name) if selected.cog_name else print("cog_name: None")
            #print("short_doc: "+selected.short_doc) if selected.short_doc else print("short_doc: None")
            #print("signature: "+selected.signature) if selected.signature else print("signature: None")


            if selection is None:
                embed = discord.Embed(title=translate(ctx.guild.id, "help.title"), color=0x55FF55)
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
                    else: embed.add_field(name=translate(ctx.guild.id, "help.uncategorized"), value=(", ".join(categories[i]['cmds'])), inline=False)
                embed.set_footer(text=translate(ctx.guild.id, "help.footer"))
                await ctx.send(embed=embed)
            elif selection_c in self.cmds_categories:
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
        self.fg_response = requests.request("GET", self.fg_request_url, headers=self.fg_request_headers)
        rj = self.fg_response.json()
        current = []
        for i in range(len(rj["freeGames"]["current"])):
            if rj["freeGames"]["current"][-i]["promotions"] and rj["freeGames"]["current"][-i]["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["discountSetting"]["discountPercentage"] == 0:
                current.append(rj["freeGames"]["current"][-i])

        for fg in current:
            try:
                free_until = fg["price"]["lineOffers"][0]["appliedRules"][0]["endDate"]
            except:
                free_until = fg["expiryDate"]
                
            embed = discord.Embed(title=fg["title"], url=("https://www.epicgames.com/store/pl/p/"+fg["title"].replace(" ", "-").lower()))
            embed.set_author(name="Darmowa giera tygodnia:", icon_url=client.user.avatar_url)
            embed.add_field(name="Darmowa od", value=useful.better_date(fg["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["startDate"]), inline=False)
            embed.add_field(name="Darmowa do", value=useful.better_date(free_until), inline=False)
            embed.set_thumbnail(url="https://cdn2.pu.nl/media/sven/epicgameslogo.png")

            for image in fg["keyImages"]:
                if image["type"] == "OfferImageWide":
                    embed.set_image(url=image["url"].replace(" ","%20"))

            embed.set_footer(text="Kliknij na nazwę aby przejść do sklepu")
            embed.timestamp = datetime.utcnow()

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
        await ctx.send(pytesseract.image_to_string(img, lang="pol"))
        
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
    
def setup(client):
    client.add_cog(Utilities(client))