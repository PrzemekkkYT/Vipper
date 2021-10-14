import discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def spamuser(self, ctx, count, memid, *, content="haha spam xD"):
        if int(count) <= 30:
            if content=="haha spam xD":
                for i in range(int(count)):
                    await ctx.send(f"<@{int(memid)}> haha spam xD")
            else:
                for i in range(int(count)):
                    await ctx.send(f"<@{int(memid)}> {content}")
        else: await ctx.send("co za dużo to nie zdrowo, możesz zaspamować maksymalnie 30 wiadomościami, sorki :)")

def setup(client):
    client.add_cog(Fun(client))