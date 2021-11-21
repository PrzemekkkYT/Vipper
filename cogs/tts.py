from cogs.music import Music
import discord
from discord.ext import commands
from gtts import gTTS, langs
import json, os
from useful import fixConfig

class TTS(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="Tekst na mowę", description="Zamienia tekst na mowę w różnych językach", usage="v!tts <treść>")
    async def tts(self, ctx, *, text):
        fixConfig(str(ctx.guild.id))
        if ctx.voice_client and ctx.message.author.voice:
                vc = ctx.voice_client
                await vc.move_to(ctx.message.author.voice.channel)
        else:
            connection = await Music.connect(Music, ctx)
            if connection is not False:
                vc = ctx.voice_client
                print("CONNECTION: ",connection)
            else: return
        
        if not os.path.exists("tts"): os.makedirs("tts")
        sound = gTTS(text=text, lang=json.load(open('config.json', 'r'))["configs"][str(ctx.guild.id)]['lang'], slow=True)
        sound.save(f"tts/tts-{ctx.guild.id}.mp3")
        
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/ffmpeg.exe", source=f"E:/DiscordBot/PyVipper/tts/tts-{ctx.guild.id}.mp3"))
        else: await ctx.send("Nie można odtworzyć, ponieważ muzyka jest odtwarzana")
        
    @commands.command(brief="Język TTS", description="Ustawia język w jakim czytany jest tekst funkcją TTS\nJeśli jako argument wpisze się \"langs\" bot wyświetli listę dostępnych języków", usage="v!ttslang <język>")
    async def ttslang(self, ctx, lang=None):
        guild_id = str(ctx.guild.id)
        fixConfig(guild_id)
            
        if lang == "langs":
            desc = ""
            for lang in langs._langs:
                desc = desc+f"\n{lang} -> {langs._langs[lang]}"
            embed = discord.Embed(title="Dostępne języki", description=desc)
            await ctx.send(embed=embed)
        elif lang is not None:
            if lang in langs._langs:
                with open("config.json", 'r+', encoding="utf-8") as json_file:
                    file_data = json.load(json_file)
                    if lang != file_data["configs"][guild_id]["lang"]:
                        file_data["configs"][guild_id]["lang"] = lang
                        json_file.seek(0)
                        json.dump(file_data, json_file, indent=4, ensure_ascii=False)
                        await ctx.send(f"Ustawiono język na {langs._langs[lang]}")
                    else: await ctx.send(f"Język {langs._langs[lang]} jest już ustawiony")
            else: await ctx.send("Nie ma takiego języka")
        else: await ctx.send(f"Aktualnie ustawiony język to: {langs._langs[json.load(open('config.json', 'r'))['configs'][guild_id]['lang']]}")
        
def setup(client):
    client.add_cog(TTS(client))