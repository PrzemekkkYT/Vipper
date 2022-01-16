from asyncio.events import new_event_loop
import enum
from cogs.music import Music
from cogs.utilities import Utilities
import discord
from discord.ext import commands
from discord.ext.commands.core import command
from discord.utils import find
import requests, asyncio, datetime, threading, random
from googletrans import Translator

class MainTimer(commands.Cog):
    def __init__(self, client):
        self.client = client

    fg_request_url = "https://free-epic-games.p.rapidapi.com/free"
    fg_request_headers = {
    'x-rapidapi-host': "free-epic-games.p.rapidapi.com",
    'x-rapidapi-key': "4a35b378bemsh2dad8e6bec18de1p119880jsne3276f501ab7"
    }
    fg_response = requests.request("GET", fg_request_url, headers=fg_request_headers)
    
    initEvents = {
        "barka": False,
        "hejnal": False,
        "freegames": False,
        "facts": False
    }
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.checkTime()
        
    def checkTime(self):
        t1 = threading.Timer(1, self.checkTime)
        t1.daemon = True
        t1.start()
        now = datetime.datetime.now()

        current_time = now.strftime("%H:%M:%S")
        if current_time=="21:37:00" or self.initEvents["barka"]:
            from cogs.music import playqueue
            print("Godzina Papieska")
            self.initEvents["barka"] = False
            asyncio.run_coroutine_threadsafe(Music.interruptListening(self, commands.Context, "https://www.youtube.com/watch?v=_o9mZ_DVTKA", playqueue), self.client.loop)
        elif current_time=="12:00:00" or self.initEvents["hejnal"]:
            from cogs.music import playqueue
            print("Hejnał Mariacki")
            self.initEvents["hejnal"] = False
            asyncio.run_coroutine_threadsafe(Music.interruptListening(self, commands.Context, "https://www.youtube.com/watch?v=WVQbxXvyG7A", playqueue), self.client.loop)
        elif (current_time=="18:00:00" and datetime.datetime.today().weekday()==3) or self.initEvents["freegames"]:
            self.initEvents["freegames"] = False
            print("Init freegames")
            asyncio.run_coroutine_threadsafe(Utilities.postcurrentfg(Utilities, self.client), self.client.loop)
        elif current_time=="23:00:00" or self.initEvents["facts"]:
            self.initEvents["facts"] = False
            with open("facts.txt", "r+", encoding="utf-8") as file:
                content = [k.strip("\n") for k in file.readlines()]
                rand = random.randint(0, len(content))
                fact = content[rand]
                file.seek(0)
                for num, line in enumerate(content):
                    if num != rand:
                        file.write(f"{line}\n")
                print(f"{datetime.datetime.today()}: {fact}")
                asyncio.run_coroutine_threadsafe(self.client.get_user(183242057882664961).send(f"Ciekawostka dnia:\n{Translator(service_urls = ['translate.google.com']).translate(fact, dest='pl').text}"), self.client.loop)
                

            
    @commands.command(hidden=True)
    async def initevent(self, ctx, event:str):
        if event.lower()=="barka":
            self.initEvents["barka"] = True
        elif event.lower()=="hejnal":
            self.initEvents["hejnal"] = True
        elif event.lower()=="freegames":
            self.initEvents["freegames"] = True
        elif event.lower()=="facts":
            self.initEvents["facts"] = True
        else:
            await ctx.send("Nie znaleziono podanego eventu")
        
def setup(client):
    client.add_cog(MainTimer(client))