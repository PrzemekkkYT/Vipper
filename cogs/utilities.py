import discord
from discord.ext import commands
from discord.utils import find
import traceback

class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    cmds = []
    cmds_names = []
    cmds_categories = []

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

    @commands.command()
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
                        if self.cmds[j].cog_name == self.cmds_categories[i]:
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

def setup(client):
    client.add_cog(Utilities(client))