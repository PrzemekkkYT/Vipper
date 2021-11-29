import datetime
import discord
from discord.ext import commands
from datetime import date, timezone
import os, json, io, useful
from discord.flags import MemberCacheFlags
from discord.role import Role
from useful import translate

class Logs(commands.Cog):
    def __init__(self, client):
        self.client = client

    activelogsbool = True

    #czy bot ma rejestrować wszystkie konwersacje na serwerze
    @commands.command(brief="activelogs.brief", description="activelogs.description", usage="activelogs.usage")
    async def activelogs(self, ctx):
        global activelogsbool
        if self.activelogsbool:
            self.activelogsbool = False
            await ctx.send(translate(ctx.guild.id, "activelogs.stopreg"))
        else:
            self.activelogsbool = True
            await ctx.send(translate(ctx.guild.id, "activelogs.startreg"))

    @commands.command(brief="downloadlog.brief", description="downloadlog.description", usage="downloadlog.usage")
    async def downloadlog(self, ctx, udate, type=None):
        if ctx.guild:
            path_chat = 'logs/chat/C-{0}-{1}.json'.format(ctx.guild.id, udate)
            path_guild = 'logs/guild/G-{0}-{1}.json'.format(ctx.guild.id, udate)
            if os.path.exists(path_chat): filedata_chat = io.BytesIO(open(path_chat, "rb").read())
            if os.path.exists(path_guild): filedata_guild = io.BytesIO(open(path_guild, "rb").read())
            if type is None:
                if os.path.exists(path_chat):
                    await ctx.send(content=translate(ctx.guild.id, "downloadlog.chat", [udate]), file=discord.File(filedata_chat, filename=path_chat[9:]))
                elif os.path.exists(path_guild):
                    await ctx.send(content=translate(ctx.guild.id, "downloadlog.guild", [udate]), file=discord.File(filedata_guild, filename=path_chat[10:]))
                else: await ctx.send(translate(ctx.guild.id, "downloadlog.fail", [udate]))
            elif type=="chat":
                if os.path.exists(path_chat):
                    await ctx.send(translate(ctx.guild.id, "downloadlog.chat", [udate]), file=discord.File(filedata_chat, filename=path_chat[9:]))
                else: await ctx.send(translate(ctx.guild.id, "downloadlog.fail", [udate]))
            elif type=="guild":
                if os.path.exists(path_guild):
                    await ctx.send(translate(ctx.guild.id, "downloadlog.guild", [udate]), file=discord.File(filedata_guild, filename=path_chat[10:]))
                else: await ctx.send(translate(ctx.guild.id, "downloadlog.fail", [udate]))
            else: await ctx.send(translate(ctx.guild.id, "downloadlog.nocategory"))

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
        message_ca = useful.utc_to_local(message.created_at.utcnow())
        path = "logs/chat/C-{0}-{1}.json".format(message.guild.id, today)

        message_info = self.json_message_info(message, message_ca, "send")
        if self.activelogsbool:
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
        before_message_ca = useful.utc_to_local(before.created_at.utcnow())
        after_message_ea = useful.utc_to_local(after.created_at.utcnow())
        path = "logs/chat/C-{0}-{1}.json".format(after.guild.id, today)

        message_info = self.json_message_info(after, after_message_ea, "edit")
        message_info["message_ca"] = {"before":str(before_message_ca), "after":str(after_message_ea)}
        message_info["content"] = {"before":str(before.content), "after":str(after.content)}
        if self.activelogsbool:
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
        message_ca = useful.utc_to_local(message.created_at.utcnow())
        path = "logs/chat/C-{0}-{1}.json".format(message.guild.id, today)

        message_info = self.json_message_info(message, message_ca, "delete")
        if self.activelogsbool:
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
        message_ca = useful.utc_to_local(reaction.message.created_at.utcnow())
        message = reaction.message
        path = "logs/chat/C-{0}-{1}.json".format(message.guild.id, today)

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
        if self.activelogsbool:
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
        message_ca = useful.utc_to_local(reaction.message.created_at.utcnow())
        message = reaction.message
        path = "logs/chat/C-{0}-{1}.json".format(message.guild.id, today)

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
        if self.activelogsbool:
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
        message_ca = useful.utc_to_local(message.created_at.utcnow())
        message = message
        path = "logs/chat/C-{0}-{1}.json".format(message.guild.id, today)

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
        if self.activelogsbool:
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
        path = "logs/guild/G-{0}-{1}.json".format(channel.guild.id, today)

        changed_roles = []
        for ch_role in channel.changed_roles:
            changed_roles.append({
                "id":str(ch_role.id),
                "name":str(ch_role.name),
                "mention":str(ch_role.mention),
                "position":str(ch_role.position),
                "color":str(ch_role.color)
            })
        
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

        if self.activelogsbool:
            guild = channel.guild
            if guild:
                if not os.path.exists(path) or os.path.getsize(path)<=0:
                    with open(path, 'a', encoding="utf-8") as json_file: json.dump({"logs":[]}, json_file, indent=4)
                with open(path, 'r+', encoding="utf-8") as json_file:
                    file_data = json.load(json_file)
                    file_data["logs"].append(channel_info)
                    json_file.seek(0)
                    json.dump(file_data, json_file, indent=4, ensure_ascii=False)
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        today = date.today()
        channel_ca = channel.created_at.replace(hour=(channel.created_at.hour+2))
        path = "logs/guild/G-{0}-{1}.json".format(channel.guild.id, today)

        changed_roles = []
        for ch_role in channel.changed_roles:
            changed_roles.append({
                "id":str(ch_role.id),
                "name":str(ch_role.name),
                "mention":str(ch_role.mention),
                "position":str(ch_role.position),
                "color":str(ch_role.color)
            })
        
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
            "deleted_at":str(datetime.datetime.now()),
            "category":str(channel.category),
            "position":str(channel.position),
            "overwrites":overwrites,
            "permissions_synced":str(channel.permissions_synced),
            "changed_roles":changed_roles
        }

        if self.activelogsbool:
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