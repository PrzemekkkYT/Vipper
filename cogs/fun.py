from asyncio.events import new_event_loop
from cogs.music import FFMPEG_OPTIONS, Music
import discord
from discord.ext import commands
from discord.ext.commands import context
from discord.utils import find
import threading, datetime, asyncio

class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.checkTime()

    def checkTime(self):
        t1 = threading.Timer(1, self.checkTime)
        t1.daemon = True
        t1.start()
        now = datetime.datetime.now()

        current_time = now.strftime("%H:%M:%S")
        if current_time=="21:37:00":
            print("godzina")
            asyncio.run_coroutine_threadsafe(self.barkaTime(), self.client.loop)
        elif current_time=="21:38:00":
            for client in self.client.voice_clients:
                    client.stop()
                    asyncio.run_coroutine_threadsafe(client.disconnect(), self.client.loop)

    async def barkaTime(self):
        vcs = []
        for guild in self.client.guilds:
            print("guild.id:",guild.id)
            vcs.append(find(lambda v: len(v.members)>0, guild.voice_channels))
        for client in self.client.voice_clients:
                    client.stop()
                    await client.disconnect()
        for vc in vcs:
            if vc:
                voice = await vc.connect()
                print("połączono z",vc.guild.id)
                song = Music.song_search(self, "https://www.youtube.com/watch?v=_o9mZ_DVTKA")
                print("voice",voice)
                voice.play(discord.FFmpegPCMAudio(song['source'], **FFMPEG_OPTIONS))
                print("puszczono barkę!")
            else: print("brak użytkowników na kanałach głosowych")


def setup(client):
    client.add_cog(Fun(client))