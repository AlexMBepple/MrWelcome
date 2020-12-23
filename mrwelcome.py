#  File:        mrwelcome.py
#  Purpose:     Implementation of our discord welcome bot
#
#  Authors:     Ryley McRae and Alex Bepple
#  Date:        December 19, 2020

import discord
import asyncio
import pickle
import time
import youtube_dl
import os
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

# get the TOKEN
tokenfile = open(r"C:\Programs\mrwelcome\very_Important.txt", "r")
TOKEN = tokenfile.readline()
# print(TOKEN)

# set the command prefix
mrwelcome = commands.Bot(command_prefix='.', intents=intents)

# creats a bot variable of an empty dictionary
# (basically a global variable for bots)
mrwelcome.d = {}


# ready check and dict import
@mrwelcome.event
async def on_ready():
    print('Mr.Welcome is ready to welcome.')
    # reads the dictionary.pickle file and creates a dictionary ADT for the
    # id and url pairs
    with open(r"C:\Programs\mrwelcome\Dictionary.pickle", 'rb') as handle:
        mrwelcome.d = pickle.load(handle)
    print(mrwelcome.d)


# adds mrwelcome to vc when someone joins
@mrwelcome.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None and member.id != 789991118443118622:
        intro_there = os.path.isfile("intro.mp3")
        if intro_there:
            print('removing')
            os.remove("intro.mp3")

        vc = after.channel
        await vc.connect()
        voice = member.guild.voice_client
        print(voice)

        if voice is not None:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([mrwelcome.d[member.id]])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file, "intro.mp3")
            voice.play(discord.FFmpegPCMAudio("intro.mp3"))
            time.sleep(7.5)  # 7500 milliseconds max
            await voice.disconnect()
        else:
            print('discord.Intents.members is likely False.')


# join command
@mrwelcome.command()
async def join(ctx):
    if ctx.author.voice is None:
        emoji = '❕'
        await ctx.message.add_reaction(emoji)
        await ctx.send('You must be connected to a voice channel to use that command.')
    else:
        channel = ctx.author.voice.channel
        return await channel.connect()


# leave command
@mrwelcome.command()
async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.send('The bot is not currently connected to a voice channel.')
    channel = ctx.author.voice.channel
    if channel is not None:
        ctx.send('Attempting to leave...')
        await ctx.voice_client.disconnect()


# terminate command
@mrwelcome.command()
async def terminate(ctx):
    emoji = '❌'
    await ctx.message.add_reaction(emoji)
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
    await mrwelcome.close()
    time.sleep(0.1)  # necessary due to asyncio bug in python3.9


# terminate error catch
@terminate.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        emoji = '🛑'
        await ctx.message.add_reaction(emoji)
        await ctx.send('Sorry, you do not have the necessary role to execute this command.')
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send('Sorry, I cant run this command from a private message!')


# Add intro
@mrwelcome.command()
@commands.has_permissions(manage_messages=True)
async def add_intro(ctx, url):
    if "youtu" not in url:
        await ctx.send('URL must be a valid youtube link')
    else:
        # updates or adds id and url to dictionary ADT
        mrwelcome.d[ctx.author.id] = url
        print(mrwelcome.d)
        # then update dictionary file
        with open(r"C:\Programs\mrwelcome\Dictionary.pickle", 'wb') as handle:
            pickle.dump(mrwelcome.d, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # Adds a reaction to the message
        emoji = '\N{THUMBS UP SIGN}'
        # or '\U0001f44d' or '👍'
        await ctx.message.add_reaction(emoji)


# add intro error catch
@add_intro.error
async def clear_add_intro_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('please provide a url as an argument')


# starts mrwelcome
mrwelcome.run(TOKEN)
