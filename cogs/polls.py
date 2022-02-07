import discord
from discord.ext import commands
from discord_components import Button
import threading, json, asyncio
from datetime import datetime, timedelta
from useful import fixPolls, translate

class Polls(commands.Cog):
    def __init__(self, client):
        self.client = client
        self._loop = asyncio.get_event_loop()
    
    # @commands.Cog.listener()
    # async def on_ready(self):
    #     self.checkTime()
    
    def checkTime(self, time, message):
        print(time, message.embeds[0].title)
        #await message.edit(components=[])
        #asyncio.run_coroutine_threadsafe(message.edit(embed=discord.Embed(title="jd", description="jd123")), loop=self.client.loop)
        embed = message.embeds[0].copy()
        embed.clear_fields()
        with open("polls.json", "r+", encoding="utf-8") as file:
            guild_id = str(message.guild.id)
            msg_id = str(message.id)
            polls_data = json.load(file)
            full = 0
            for option in polls_data[guild_id][msg_id]['options']:
                full += float(polls_data[guild_id][msg_id]['options'][option])
            embed.description = translate(message.guild.id, "poll.allvotes", [int(full)])
            for option in polls_data[guild_id][msg_id]['options']:
                percent = ((float(polls_data[guild_id][msg_id]['options'][option])/full)*100)
                progress_bar = ""
                for i in range(1, 21):
                    if percent < i*5:
                        progress_bar += "░"
                    else: progress_bar += "▓"
                embed.add_field(name=(option+': %.2f'%percent+"%"), value=progress_bar, inline=False)
        embed.set_footer(text=translate(message.guild.id, "poll.ended", [datetime.strftime(datetime.now(), '%d.%m.%Y'), datetime.strftime(datetime.now(), '%H:%M')]))
        asyncio.run_coroutine_threadsafe(message.edit(embed=embed, components=[]), loop=self.client.loop)


    @commands.command(brief="initpoll.brief", description="initpoll.description", usage="initpoll.usage")
    async def initpoll(self, ctx, time, *, options):
        try: int(time[:-1])
        except:
            await ctx.send(translate(ctx.guild.id, "initpoll.wrongtime"))
            return
        options = options.split(" | ")
        name = options.pop(0)
        print(options)
        endTime = datetime.now()
        match time[-1]:
            case "m":
                if int(time[:-1])>=5:
                    endTime += timedelta(minutes=int(time[:-1]))
                    time = int(time[:-1])*60
                    await ctx.send(endTime)
                else:
                    await ctx.send(translate(ctx.guild.id, "initpoll.tooshort"))
                    return
            case "h":
                endTime += timedelta(hours=int(time[:-1]))
                time = int(time[:-1])*60*60
                await ctx.send(endTime)
            case "d":
                endTime += timedelta(days=int(time[:-1]))
                time = int(time[:-1])*60*60*24
                await ctx.send(endTime)
            case "w":
                endTime += timedelta(weeks=int(time[:-1]))
                time = int(time[:-1])*60*60*24*7
                await ctx.send(endTime)
            case _:
                await ctx.send(translate(ctx.guild.id, "initpoll.wrongtime"))
                return
        components = []
        if 1 < len(options) <= 5:
            for option in options:
                components.append(Button(label=option, custom_id=option))
        else:
            await ctx.send(translate(ctx.guild.id, "initpoll.optlimit"))
            return
            
        embed = discord.Embed(title=name, description=translate(ctx.guild.id, "poll.allvotes", [0]))
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.set_footer(text=translate(ctx.guild.id, "initpoll.willend", [datetime.strftime(endTime, '%d.%m.%Y'), datetime.strftime(endTime, '%H:%M')]))
        for option in options:
            embed.add_field(name=(option+" 0.00%"), value=("░"*20), inline=False)
        msg = await ctx.send(embed=embed, components=[components])
        #self.polls[msg.id] = {}
        guild_id = str(ctx.guild.id)
        msg_id = str(msg.id)
        fixPolls(guild_id)
        with open("polls.json", "r+", encoding="utf-8") as file:
            file_data = json.load(file)
            if msg_id not in file_data[guild_id]: file_data[guild_id][msg_id] = {}
            if "host" not in file_data[guild_id][msg_id]: file_data[guild_id][msg_id]["host"] = str(ctx.author.id)
            if "endTime" not in file_data[guild_id][msg_id]: file_data[guild_id][msg_id]["endTime"] = str(endTime)
            if "title" not in file_data[guild_id][msg_id]: file_data[guild_id][msg_id]["title"] = name
            if "options" not in file_data[guild_id][msg_id]: file_data[guild_id][msg_id]["options"] = {}
            if "voters" not in file_data[guild_id][msg_id]: file_data[guild_id][msg_id]["voters"] = {}
            for option in options:
                file_data[guild_id][msg_id]["options"][option] = 0
            file.seek(0)
            json.dump(file_data, file, indent=4, ensure_ascii=False)
            file.close()

        self._loop.call_later(time, self.checkTime, time, msg)

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        # await interaction.respond(content=f"Button Clicked, {interaction.custom_id}")
        # await interaction.message.edit(embed=discord.Embed(title=interaction.custom_id))
        fixPolls(str(interaction.guild.id))
        with open("polls.json", "r+", encoding="utf-8") as file:
            guild_id = str(interaction.message.guild.id)
            msg_id = str(interaction.message.id)
            button_id = str(interaction.custom_id)
            user_id = str(interaction.user.id)
            polls_data = json.load(file)
            if msg_id in polls_data[guild_id]:
                if datetime.now() < datetime.strptime(polls_data[guild_id][msg_id]["endTime"], "%Y-%m-%d %H:%M:%S.%f"):
                    if user_id not in polls_data[guild_id][msg_id]["voters"]:
                        if button_id not in polls_data[guild_id][msg_id]["options"]:
                            polls_data[guild_id][msg_id]["options"][button_id] = 1
                        else: polls_data[guild_id][msg_id]["options"][button_id] += 1
                        full = 0
                        print(f"podimid: {polls_data[guild_id][msg_id]['options']}")
                        for option in polls_data[guild_id][msg_id]['options']:
                            full += float(polls_data[guild_id][msg_id]['options'][option])
                        embed = discord.Embed(title=interaction.message.embeds[0].title, description=translate(interaction.guild.id, "poll.allvotes", [int(full)]))
                        author = interaction.guild.get_member(int(polls_data[guild_id][msg_id]["host"]))
                        embed.set_author(name=author.name, icon_url=author.avatar_url)
                        endTime = polls_data[guild_id][msg_id]["endTime"].split(" ")
                        embed.set_footer(text=translate(interaction.guild.id, "initpoll.willend", [endTime[0], endTime[1][:-10]]))
                        for option in polls_data[guild_id][msg_id]['options']:
                            percent = ((float(polls_data[guild_id][msg_id]['options'][option])/full)*100)
                            progress_bar = ""
                            for i in range(1, 21):
                                if percent < i*5:
                                    progress_bar += "░"
                                else: progress_bar += "▓"
                            embed.add_field(name=(option+': %.2f'%percent+"%"), value=progress_bar, inline=False)
                        polls_data[guild_id][msg_id]["voters"][user_id] = button_id
                        await interaction.message.edit(embed=embed)
                        await interaction.respond(content=translate(interaction.guild.id, "poll.vote"))
                        file.seek(0)
                        json.dump(polls_data, file, indent=4, ensure_ascii=False)
                    else: await interaction.respond(content=translate(interaction.guild.id, "poll.answered"))
                else: await interaction.respond(content=translate(interaction.guild.id, "poll.timesup"))
            else: await interaction.respond(content=translate(interaction.guild.id, "poll.notapoll"))
            file.close()


def setup(client):
    client.add_cog(Polls(client))