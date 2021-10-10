from asyncio.events import new_event_loop
from cogs.music import Music
from cogs.utilities import Utilities
import discord
from discord.ext import commands
from discord.ext.commands.core import command
from discord.utils import find
import requests, asyncio, datetime, threading

class MainTimer(commands.Cog):
    def __init__(self, client):
        self.client = client

    fg_request_url = "https://free-epic-games.p.rapidapi.com/free"
    fg_request_headers = {
        'x-rapidapi-host': "free-epic-games.p.rapidapi.com",
        'x-rapidapi-key': "4a35b378bemsh2dad8e6bec18de1p119880jsne3276f501ab7"
    }
    fg_response = requests.request("GET", fg_request_url, headers=fg_request_headers)
    
    initBarkaB = False
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.checkTime()
        
    def checkTime(self):
        t1 = threading.Timer(1, self.checkTime)
        t1.daemon = True
        t1.start()
        now = datetime.datetime.now()

        current_time = now.strftime("%H:%M:%S")
        if current_time=="21:37:00" or self.initBarkaB:
            from cogs.music import playqueue
            print("godzina")
            self.initBarkaB = False
            asyncio.run_coroutine_threadsafe(Music.interruptListening(self, commands.Context, "https://www.youtube.com/watch?v=_o9mZ_DVTKA", playqueue), self.client.loop)
        elif current_time=="19:00:00" and datetime.datetime.weekday==3:
            self.fg_response = requests.request("GET", self.fg_request_url, headers=self.fg_request_headers)
            asyncio.run_coroutine_threadsafe(Utilities.postcurrentfg(Utilities, self.client), self.client.loop)
            
    @commands.command()
    async def initBarka(self, ctx):
        self.initBarkaB = True
        
def setup(client):
    client.add_cog(MainTimer(client))