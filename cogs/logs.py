import discord
from discord.ext import commands
from datetime import date, timezone
import random, os, json

from discord.flags import MemberCacheFlags
from discord.role import Role

class Logs(commands.Cog):
    def __init__(self, client):
        self.client = client

    saveconvobool = True

    def utc_to_local(self, utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    #czy bot ma rejestrować wszystkie konwersacje na serwerze
    @commands.command()
    async def saveconvo(self, ctx):
        global saveconvobool
        if self.saveconvobool:
            self.saveconvobool = False
            await ctx.send("Ta konwersacja nie będzie już rejestrowana")
        else:
            self.saveconvobool = True
            await ctx.send("Rozpoczynam rejestrowanie konwersacji")

    @commands.command()
    async def downloadlog(self, ctx, udate, type=None):
        if ctx.guild:
            path_chat = 'logs/chat/{0}-{1}.txt'.format(ctx.guild.id, udate)
            path_chat_embed = 'logs/chat/{0}-{1}-Embeds.txt'.format(ctx.guild.id, udate)
            path_guild = 'logs/guild/{0}-{1}.txt'.format(ctx.guild.id, udate)
            if type is None:
                await ctx.send(file=discord.File('test/vipper-avatar.png'))
                if os.path.exists(path_chat):
                    await ctx.send("Logi czatów:", file=discord.File(path_chat))
                if os.path.exists(path_chat_embed):
                    await ctx.send("Logi czatów (Embed):", file=discord.File(path_chat_embed))
                if os.path.exists(path_guild):
                    await ctx.send("Logi serwera:", file=discord.File(path_guild))
            if type=="chat":
                if os.path.exists(path_chat):
                    await ctx.send("Logi czatów:", file=discord.File(path_chat))
                if os.path.exists(path_chat_embed):
                    await ctx.send("Logi czatów (Embed):", file=discord.File(path_chat_embed))
            if type=="guild":
                if os.path.exists(path_guild):
                    await ctx.send("Logi serwera:", file=discord.File(path_guild))

    def json_message_info(self, message, message_ca, type):
        attachments = []
        for attachment in message.attachments:
            attachments.append({
                "id":attachment.id,
                "filename":attachment.filename,
                "url":attachment.url,
                "content_type":attachment.content_type,
                "height":attachment.height,
                "width":attachment.width,
                "size":attachment.size,
                "proxy_url":attachment.proxy_url
            })
        embeds = []
        for embed in message.embeds:
            fields = []
            for field in embed.fields:
                fields.append({
                    "name":field.name,
                    "value":field.value,
                    "inline":field.inline
                })
            embeds.append({
                "author":{"name":str(embed.author.name), "url":str(embed.author.url), "icon_url":str(embed.author.icon_url)},
                "colour":str(embed.colour),
                "title":str(embed.title),
                "description":str(embed.description),
                "fields":fields,
                "footer":{"text":str(embed.footer.text), "icon_url":str(embed.footer.icon_url)},
                "image":str(embed.image.url),
                "thumbnail":str(embed.thumbnail.url),
                "type":str(embed.type),
                "url":str(embed.url),
                "video":str(embed.video.url)
            })
        reactions = []
        for reaction in message.reactions:
            reactions.append({
                "count":reaction.count,
                "custom_emoji":reaction.custom_emoji,
                "emoji":str(reaction.emoji),
                "me":reaction.me
            })
        message_info = {
            "action_type":f"message.{type}",
            "jump_url":message.jump_url,
            "message_id":message.id,
            "message_ca":str(message_ca),
            "channel_name":message.channel.name,
            "channel_id":message.channel.id,
            "author":str(message.author),
            "content":message.content,
            "attachments":attachments,
            "embeds":embeds,
            "reactions":reactions
        }
        return message_info

    #rejestracja konwersacji do pliku tekstowego
    @commands.Cog.listener()
    async def on_message(self, message):
        today = date.today()
        message_ca = self.utc_to_local(message.created_at.utcnow())
        path = "logs/chat/{0}-{1}.json".format(message.guild.id, today)

        message_info = self.json_message_info(message, message_ca, "send")
        if self.saveconvobool:
            guild = message.guild
            if guild:
                if not os.path.exists(path) or os.path.getsize(path)<=0:
                    with open(path, 'a', encoding="utf-8") as json_file: json.dump({"logs":[]}, json_file, indent=4)
                with open(path, 'r+', encoding="utf-8") as json_file:
                    file_data = json.load(json_file)
                    file_data["logs"].append(message_info)
                    json_file.seek(0)
                    json.dump(file_data, json_file, indent=4, ensure_ascii=False)

    #rejestracja do pliku tekstowego czy edytowano wiadomość
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        today = date.today()
        before_message_ca = self.utc_to_local(before.created_at.utcnow())
        after_message_ea = self.utc_to_local(after.created_at.utcnow())
        path = "logs/chat/{0}-{1}.json".format(after.guild.id, today)

        message_info = self.json_message_info(after, after_message_ea, "edit")
        message_info["message_ca"] = {"before":str(before_message_ca), "after":str(after_message_ea)}
        message_info["content"] = {"before":str(before.content), "after":str(after.content)}
        if self.saveconvobool:
            guild = after.guild
            if guild:
                if not os.path.exists(path) or os.path.getsize(path)<=0:
                    with open(path, 'a', encoding="utf-8") as json_file: json.dump({"logs":[]}, json_file, indent=4)
                with open(path, 'r+', encoding="utf-8") as json_file:
                    file_data = json.load(json_file)
                    file_data["logs"].append(message_info)
                    json_file.seek(0)
                    json.dump(file_data, json_file, indent=4, ensure_ascii=False)

    #rejestracja do pliku tekstowego czy usunięto wiadomość
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        today = date.today()
        message_ca = self.utc_to_local(message.created_at.utcnow())
        path = "logs/chat/{0}-{1}.json".format(message.guild.id, today)

        message_info = self.json_message_info(message, message_ca, "delete")
        if self.saveconvobool:
            guild = message.guild
            if guild:
                if not os.path.exists(path) or os.path.getsize(path)<=0:
                    with open(path, 'a', encoding="utf-8") as json_file: json.dump({"logs":[]}, json_file, indent=4)
                with open(path, 'r+', encoding="utf-8") as json_file:
                    file_data = json.load(json_file)
                    file_data["logs"].append(message_info)
                    json_file.seek(0)
                    json.dump(file_data, json_file, indent=4, ensure_ascii=False)
    
    #rejestracja do pliku tekstowego czy dodano reakcję do wiadomości
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        today = date.today()
        message_ca = self.utc_to_local(reaction.message.created_at.utcnow())
        message = reaction.message
        path = "logs/chat/{0}-{1}.json".format(message.guild.id, today)

        message_info = self.json_message_info(message, message_ca, "reaction.add")
        message_info["reaction.added"] = {
            "count": reaction.count,
            "custom_emoji": reaction.custom_emoji,
            "emoji": str(reaction.emoji),
            "me": reaction.me,
            "user":{
                "name":user.name,
                "mention":user.mention,
                "bot":user.bot
            }
        }
        if self.saveconvobool:
            guild = message.guild
            if guild:
                if not os.path.exists(path) or os.path.getsize(path)<=0:
                    with open(path, 'a', encoding="utf-8") as json_file: json.dump({"logs":[]}, json_file, indent=4)
                with open(path, 'r+', encoding="utf-8") as json_file:
                    file_data = json.load(json_file)
                    file_data["logs"].append(message_info)
                    json_file.seek(0)
                    json.dump(file_data, json_file, indent=4, ensure_ascii=False)
                    
    #rejestracja do pliku tekstowego czy usunięto reakcję z wiadomości
    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        today = date.today()
        message_ca = self.utc_to_local(reaction.message.created_at.utcnow())
        message = reaction.message
        path = "logs/chat/{0}-{1}.json".format(message.guild.id, today)

        message_info = self.json_message_info(message, message_ca, "reaction.remove")
        message_info["reaction.removed"] = {
            "count": reaction.count,
            "custom_emoji": reaction.custom_emoji,
            "emoji": str(reaction.emoji),
            "me": reaction.me,
            "user":{
                "name":user.name,
                "mention":user.mention,
                "bot":user.bot
            }
        }
        if self.saveconvobool:
            guild = message.guild
            if guild:
                if not os.path.exists(path) or os.path.getsize(path)<=0:
                    with open(path, 'a', encoding="utf-8") as json_file: json.dump({"logs":[]}, json_file, indent=4)
                with open(path, 'r+', encoding="utf-8") as json_file:
                    file_data = json.load(json_file)
                    file_data["logs"].append(message_info)
                    json_file.seek(0)
                    json.dump(file_data, json_file, indent=4, ensure_ascii=False)
    @commands.Cog.listener()
    async def on_reaction_clear(self, message, reactions):
        today = date.today()
        message_ca = self.utc_to_local(message.created_at.utcnow())
        message = message
        path = "logs/chat/{0}-{1}.json".format(message.guild.id, today)

        message_info = self.json_message_info(message, message_ca, "reaction.remove")
        reactions_removed = []
        for reaction in reactions:
            reactions_removed.append({
            "count": reaction.count,
            "custom_emoji": reaction.custom_emoji,
            "emoji": str(reaction.emoji),
            "me": reaction.me
        })
        message_info["reactions.removed"] = reactions_removed
        if self.saveconvobool:
            guild = message.guild
            if guild:
                if not os.path.exists(path) or os.path.getsize(path)<=0:
                    with open(path, 'a', encoding="utf-8") as json_file: json.dump({"logs":[]}, json_file, indent=4)
                with open(path, 'r+', encoding="utf-8") as json_file:
                    file_data = json.load(json_file)
                    file_data["logs"].append(message_info)
                    json_file.seek(0)
                    json.dump(file_data, json_file, indent=4, ensure_ascii=False)
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        today = date.today()
        channel_ca = channel.created_at.replace(hour=(channel.created_at.hour+2))
        path = "logs/guild/{0}-{1}.json".format(channel.guild.id, today)

        changed_roles = []
        for ch_role in channel.changed_roles:
            changed_roles.append({
                "id":str(ch_role.id),
                "name":str(ch_role.name),
                "mention":str(ch_role.mention),
                "position":str(ch_role.position),
                "color":str(ch_role.color)
            })

        print("============================================ OVERWRITE PRINT TEST BYQ",list(channel.overwrites))
        
        overwrites = []
        for overwrite in channel.overwrites:
            if isinstance(overwrite, discord.role.Role):
                overwrites.append({"role":str(overwrite)})
            else:
                overwrites.append({"member":str(overwrite)})

        channel_info = {
            "name":str(channel.name),
            "mention":str(channel.mention),
            "created_at":str(channel_ca),
            "category":str(channel.category),
            "position":str(channel.position),
            "overwrites":overwrites,
            "permissions_synced":str(channel.permissions_synced),
            "changed_roles":changed_roles
        }

        if self.saveconvobool:
            guild = channel.guild
            if guild:
                if not os.path.exists(path) or os.path.getsize(path)<=0:
                    with open(path, 'a', encoding="utf-8") as json_file: json.dump({"logs":[]}, json_file, indent=4)
                with open(path, 'r+', encoding="utf-8") as json_file:
                    file_data = json.load(json_file)
                    file_data["logs"].append(channel_info)
                    json_file.seek(0)
                    json.dump(file_data, json_file, indent=4, ensure_ascii=False)

def setup(client):
    client.add_cog(Logs(client))