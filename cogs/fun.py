import discord
from discord.ext import commands
from useful import translate

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="spamuser.brief", description="spamuser.description", usage="spamuser.usage")
    async def spamuser(self, ctx, count, memid, delmsg:str="false", *, content="haha spam xD"):
        if delmsg.lower()=="true":
            await ctx.message.delete()
        if int(count) <= 30:
            for i in range(int(count)):
                await ctx.send(f"<@{int(memid)}> {content}")
            print(f"Zakończono spam użytkownika {memid}")
        else: await ctx.send(translate(ctx.guild.id, "spamuser.toomany"))
        
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.id == 725711519765233676:
            if after.display_name != "Stópkasz":
                await after.edit(nick="Stópkasz")
    
def setup(client):
    client.add_cog(Fun(client))