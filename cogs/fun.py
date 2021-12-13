import discord
from discord.ext import commands
from useful import translate, morse

nicks = {}

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        with open("nicks.txt", encoding="utf-8") as file:
            file_data = file.read().splitlines()
            for line in file_data:
                nickopt = line.split("::")
                nicks[nickopt[0]] = nickopt[1]
            file.close()
    
    @commands.command(brief="spamuser.brief", description="spamuser.description", usage="spamuser.usage")
    async def spamuser(self, ctx, count, memid, delmsg:str="false", *, content="haha spam xD"):
        if delmsg.lower()=="true":
            await ctx.message.delete()
        if int(count) <= 30:
            for i in range(int(count)):
                await ctx.send(f"<@{int(memid)}> {content}")
            print(f"Zakończono spam użytkownika {memid}")
        else: await ctx.send(translate(ctx.guild.id, "spamuser.toomany"))
    
    @commands.command(brief="morse.brief", description="morse.description", usage="morse.usage")
    async def morse(self, ctx, *, text:str):
        try:
            reverse_morse = {value : key for (key, value) in morse.items()}
            result = ""
            for word in text:
                for char in word:
                    result += (reverse_morse[char]+" ")
            await ctx.send(result)
        except:
            text = text.split(" ")
            result = ""
            for char in text:
                result += morse[char]
            await ctx.send(result)
        
    # @commands.command()
    # async def nickreload(self, ctx):
    #     with open("nicks.txt", encoding="utf-8") as file:
    #         file_data = file.read().splitlines()
    #         for line in file_data:
    #             nickopt = line.split("::")
    #             nicks[nickopt[0]] = nickopt[1]
    #         file.close()
    
    # @commands.command()
    # async def nicktest(self, ctx):
    #     print(nicks)
    #     for nick in nicks:
    #         print(nick)
    #     if any(str(ctx.message.author.id)==nick for nick in nicks):
    #         print("ok")
    
    # @commands.Cog.listener()
    # async def on_member_update(self, before, after):
    #     if any(str(after.id)==nick for nick in nicks):
    #         if after.display_name != nicks[str(after.id)]:
    #             await after.edit(nick=nicks[str(after.id)])
    
def setup(client):
    client.add_cog(Fun(client))