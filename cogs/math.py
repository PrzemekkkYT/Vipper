import discord
from discord.ext import commands
from useful import VMath, translate

class Math(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(brief="pfkwconv.brief", description="pfkwconv.description", usage="pfkwconv.usage")
    async def pfkwconv(self, ctx, type:str):
        if type=="i>o" or type=="f>s":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.f"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.itoo(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        elif type=="i>k" or type=="f>v":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.f"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.itok(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        elif type=="o>i" or type=="s>f":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.s"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.otoi(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        elif type=="o>k" or type=="s>v":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.s"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.otok(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        elif type=="k>i" or type=="v>f":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.v"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.ktoi(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        elif type=="k>o" or type=="v>s":
            try:
                await ctx.send(translate(ctx.guild.id, "pfkwconv.v"))
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.ktoo(message.content))
            except: await ctx.send(translate(ctx.guild.id, "pfkwconv.not", [message.content]))
        else: await ctx.send(translate(ctx.guild.id, "pfkwconv.noopt"))
        
        
    
def setup(client):
    client.add_cog(Math(client))