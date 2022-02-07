import discord
from discord.ext import commands
from useful import VMath, translate

class Math(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(brief="pfkwconv.brief", description="pfkwconv.description", usage="pfkwconv.usage")
    async def pfkwconv(self, ctx, conversion:str):
        if conversion=="i>o" or conversion=="f>s":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.f"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.itoo(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        elif conversion=="i>k" or conversion=="f>v":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.f"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.itok(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        elif conversion=="o>i" or conversion=="s>f":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.s"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.otoi(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        elif conversion=="o>k" or conversion=="s>v":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.s"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.otok(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        elif conversion=="k>i" or conversion=="v>f":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.v"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.ktoi(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        elif conversion=="k>o" or conversion=="v>s":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.v"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.ktoo(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        else: await ctx.send(translate(ctx.guild.id, "pfkwconv.noopt"))
        
        
    
def setup(client):
    client.add_cog(Math(client))