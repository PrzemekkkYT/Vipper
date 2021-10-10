import discord
from discord.mentions import AllowedMentions
from discord.ext import commands
from discord.utils import find
import traceback, useful, requests, sqlite3
from datetime import date, datetime

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

    @commands.command(brief="Informacje o komendach i kategoriach", description="1. Umożliwia wyświetlenie najważniejszych informacji o:\n•komendach - Kategoria, Aliasy, Opis, Składania.\n•Kategoriach - dostępne komendy i ich krótki opis.\n2. Czytanie składni:\n•<> - argument obowiązkowy\n•[] - argument opcjonalny", usage="v!help [nazwa komendy/kategorii]")
    async def help(self, ctx, selection=None):
        try:
            selected = find(lambda s: s.name == selection, self.cmds)
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
                embed.set_footer(text="Możesz sprawdzić informacje o dowolnej komendzie lub kategorii wpisując jej nazwę jako argument. Przykład: v!help play")
                await ctx.send(embed=embed)
            elif selection_c in self.cmds_categories:
                embed = discord.Embed(title=("Kategoria: "+selection_c), color=0x55FF55)
                for i in range(len(self.cmds)):
                    if self.cmds[i].cog_name == selection_c:
                        embed.add_field(name=self.cmds[i].name, value=self.cmds[i].brief, inline=False)
                await ctx.send(embed=embed)
            elif selection in self.cmds_names:
                embed = discord.Embed(title=("Komenda: "+selection), color=0x55FF55)
                if selected.cog_name:
                    embed.add_field(name="Kategoria", value=selected.cog_name, inline=False)
                else: embed.add_field(name="Kategoria", value="Brak kategorii", inline=False)
                if selected.aliases:
                    embed.add_field(name="Aliasy", value=(', '.join(selected.aliases)))
                else: embed.add_field(name="Aliasy", value="Brak aliasów", inline=False)
                if selected.description:
                    embed.add_field(name="Opis", value=selected.description, inline=False)
                else: embed.add_field(name="Opis", value="Brak opisu", inline=False)
                if selected.usage:
                    embed.add_field(name="Składnia", value=selected.usage, inline=False)
                else: embed.add_field(name="Składnia", value="Brak składni", inline=False)
                await ctx.send(embed=embed)
        except Exception as inst:
            embed = discord.Embed(title="Nie znaleziono podanej komendy", color=0x55FF55)
            await ctx.send(embed=embed)
            print("===========! HELP TRACEBACK !===========")
            traceback.print_tb(inst.__traceback__)
            print("===========! HELP TRACEBACK !===========")

    async def postcurrentfg(self, client):
        rj = self.fg_response.json()
        current = []
        for i in range(len(rj["freeGames"]["current"])):
            if rj["freeGames"]["current"][-i]["promotions"] and rj["freeGames"]["current"][-i]["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["discountSetting"]["discountPercentage"] == 0:
                current.append(rj["freeGames"]["current"][-i])

        for fg in current:
            free_until = fg["price"]["lineOffers"][0]["appliedRules"][0]["endDate"]
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

def setup(client):
    client.add_cog(Utilities(client))