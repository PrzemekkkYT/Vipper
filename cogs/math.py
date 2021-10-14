import discord
from discord.ext import commands
from useful import VMath

class Math(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(brief="Konwerter postaci funkcji kwadratowej", description="Zamienia postać funkcji kwadratowej między ogólną, kanoniczną i iloczynową.\nTypy konwersji:\ni>o - iloczynowa na ogólną\ni>k - iloczynowa na kanoniczną\no>i - ogólna na iloczynową\no>k - ogólna na kanoniczną\nk>i - kanoniczna na iloczynową\nk>o - kanoniczna na ogólną", usage="v!pfkwconv <typ konwersji>")
    async def pfkwconv(self, ctx, type:str):
        if type=="i>o":
            try:
                await ctx.send("Podaj funkcję w postaci iloczynowej")
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.itoo(message.content))
            except: await ctx.send(f"\"{message.content}\" nie jest funkcją kwadratową.")
        elif type=="i>k":
            try:
                await ctx.send("Podaj funkcję w postaci iloczynowej")
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.itok(message.content))
            except: await ctx.send(f"\"{message.content}\" nie jest funkcją kwadratową.")
        elif type=="o>i":
            try:
                await ctx.send("Podaj funkcję w postaci ogólnej")
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.otoi(message.content))
            except: await ctx.send(f"\"{message.content}\" nie jest funkcją kwadratową.")
        elif type=="o>k":
            try:
                await ctx.send("Podaj funkcję w postaci ogólnej")
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.otok(message.content))
            except: await ctx.send(f"\"{message.content}\" nie jest funkcją kwadratową.")
        elif type=="k>i":
            try:
                await ctx.send("Podaj funkcję w postaci kanonicznej")
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.ktoi(message.content))
            except: await ctx.send(f"\"{message.content}\" nie jest funkcją kwadratową.")
        elif type=="k>o":
            try:
                await ctx.send("Podaj funkcję w postaci kanonicznej")
                message = await ctx.bot.wait_for('message', timeout=60.0)
                await ctx.send(VMath.ktoo(message.content))
            except: await ctx.send(f"\"{message.content}\" nie jest funkcją kwadratową.")
        else: await ctx.send("Nie ma takiej konwersji.")
        
        
    
def setup(client):
    client.add_cog(Math(client))