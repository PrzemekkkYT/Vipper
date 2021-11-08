import discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="Spamuje określnego użytkownika", description="Spamuje określonego użytkownika maksymalnie 30 razy określoną wiadomością\nId użytkownika można pobrać klikając na niego prawym, po czym wybrać opcję \"Kopiuj ID\"\n[Usunięcie wiadomości] = true/false usuwa wiadomość, żeby osoba spamowana nie wiedziała kto to zrobił", usage="v!spamuser <ilość> <id użytkownika> [usunięcie wiadomości] [treść spamu]")
    async def spamuser(self, ctx, count, memid, delmsg:str="false", *, content="haha spam xD"):
        if delmsg.lower()=="true":
            await ctx.message.delete()
        if int(count) <= 30:
            for i in range(int(count)):
                await ctx.send(f"<@{int(memid)}> {content}")
            print(f"Zakończono spam użytkownika {memid}")
        else: await ctx.send("co za dużo to nie zdrowo, możesz zaspamować maksymalnie 30 wiadomościami, sorki :)")

def setup(client):
    client.add_cog(Fun(client))