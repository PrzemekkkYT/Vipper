import discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def spamuser(self, ctx, count, memid):
        for i in range(int(count)):
            await ctx.send(f"<@{int(memid)}> haha spam xD")

def setup(client):
    client.add_cog(Fun(client))