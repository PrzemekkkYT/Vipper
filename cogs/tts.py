from cogs.music import Music
import discord
from discord.ext import commands
from gtts import gTTS, langs
import json

class TTS(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="Tekst na mowę", description="Zamienia tekst na mowę w różnych językach", usage="v!tts <treść>")
    async def tts(self, ctx, *, text):
        if ctx.voice_client and ctx.message.author.voice:
                vc = ctx.voice_client
                await vc.move_to(ctx.message.author.voice.channel)
        else:
            connection = await Music.connect(Music, ctx)
            if connection is not False:
                vc = ctx.voice_client
                print("CONNECTION: ",connection)
            else: return
        
        sound = gTTS(text=text, lang=json.load(open('config.json', 'r'))['lang'], slow=True)
        sound.save("tts.mp3")
        
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/ffmpeg.exe", source="E:/DiscordBot/PyVipper/tts.mp3"))
        else: await ctx.send("Nie można odtworzyć, ponieważ muzyka jest odtwarzana")
        
    @commands.command()
    async def ttslang(self, ctx, lang=None):
        if lang == "langs":
            desc = ""
            for lang in langs._langs:
                desc = desc+f"\n{lang} -> {langs._langs[lang]}"
                print(lang,langs._langs[lang])
            embed = discord.Embed(title="Dostępne języki", description=desc)
            await ctx.send(embed=embed)
        elif lang is not None:
            if lang in langs._langs:
                with open("config.json", 'r+', encoding="utf-8") as json_file:
                    file_data = json.load(json_file)
                    if lang != file_data["lang"]:
                        file_data["lang"] = lang
                        json_file.seek(0)
                        json.dump(file_data, json_file, indent=4, ensure_ascii=False)
                        await ctx.send(f"Ustawiono język na {langs._langs[lang]}")
                    else: await ctx.send(f"Język {langs._langs[lang]} jest już ustawiony")
            else: await ctx.send("Nie ma takiego języka")
        else: await ctx.send(f"Aktualnie ustawiony język to: {langs._langs[json.load(open('config.json', 'r'))['lang']]}")
        
def setup(client):
    client.add_cog(TTS(client))