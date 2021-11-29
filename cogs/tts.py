from cogs.music import Music
import discord
from discord.ext import commands
from gtts import gTTS, langs
import json, os
from useful import fixConfig, translate

class TTS(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="tts.brief", description="tts.description", usage="tts.usage")
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
        sound = gTTS(text=text, lang=json.load(open('config.json', 'r'))["configs"][str(ctx.guild.id)]['ttslang'], slow=True)
        sound.save(f"tts/tts-{ctx.guild.id}.mp3")
        
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/ffmpeg.exe", source=f"E:/DiscordBot/PyVipper/tts/tts-{ctx.guild.id}.mp3"))
        else: await ctx.send(translate(ctx.guild.id, "tts.isplaying"))
        
    @commands.command(brief="ttslang.brief", description="ttslang.description", usage="ttslang.usage")
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
                    if lang != file_data["configs"][guild_id]["ttslang"]:
                        file_data["configs"][guild_id]["ttslang"] = lang
                        json_file.seek(0)
                        json.dump(file_data, json_file, indent=4, ensure_ascii=False)
                        await ctx.send(translate(ctx.guild.id, "ttslang.setlang", [langs._langs[lang]]))
                    else: await ctx.send(translate(ctx.guild.id, "ttslang.alreadyset", [langs._langs[lang]]))
            else: await ctx.send(translate(ctx.guild.id, "ttslang.nolang"))
        else: await ctx.send(translate(ctx.guild.id, "ttslang.current", [langs._langs[json.load(open('config.json', 'r'))['configs'][guild_id]['ttslang']]]))
        
def setup(client):
    client.add_cog(TTS(client))