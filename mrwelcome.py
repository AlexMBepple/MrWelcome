#  File:        mrwelcome.py
#  Purpose:     Implementation of our discord welcome bot
#
#  Authors:     Ryley McRae and Alex Bepple
#  Date:        December 19, 2020

import discord
import pickle
import time
import youtube_dl
import os
import pprint
from discord.ext import commands

# from datetime import datetime

intents = discord.Intents.default()
intents.members = True

# get the TOKEN
tokenfile = open(r"C:\Users\User\Desktop\yes\mrwelcome\very_Important.txt", "r")
TOKEN = tokenfile.readline()
# print(TOKEN)

# set the command prefix
mrwelcome = commands.Bot(command_prefix='.', intents=intents)

# creates a bot variable of an empty dictionary
mrwelcome.d = {}
mrwelcome.meme_d = {}

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


def is_supported(url):
    extractors = youtube_dl.extractor.gen_extractors()
    for e in extractors:
        if e.suitable(url) and e.IE_NAME != 'generic':
            return True
    return False


# ready check and dict import
@mrwelcome.event
async def on_ready():
    print('Mr.Welcome is ready to welcome.')
    pp = pprint.PrettyPrinter(width=41, compact=True)
    # reads the dictionary.pickle file and creates a dictionary ADT for the
    # id and url pairs
    with open(r"C:\Users\User\Desktop\yes\mrwelcome\Dictionary.pickle", "rb") as handle:
        mrwelcome.d = pickle.load(handle)
        pp.pprint(mrwelcome.d)
    with open(r"C:\Users\User\Desktop\yes\mrwelcome\meme.pickle", 'rb') as handle1:
        mrwelcome.meme_d = pickle.load(handle1)
        pp.pprint(mrwelcome.meme_d)


# adds mrwelcome to vc when someone joins
@mrwelcome.event
async def on_voice_state_update(member, before, after):
    if member.id in mrwelcome.d and before.channel is None and after.channel is not None:
        bot_status = member.guild.me.voice
        if bot_status is None:
            vc = after.channel
            await vc.connect()
        voice = member.guild.voice_client
        if voice is not None:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([mrwelcome.d[member.id]])
                dictMeta = ydl.extract_info(mrwelcome.d[member.id])
                duration = int(dictMeta["duration"])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file, "intro.mp3")
            voice.play(discord.FFmpegPCMAudio("intro.mp3"))
            if duration > 7:
                time.sleep(7.5)  # 7500 milliseconds max
            else:
                time.sleep(duration+0.5)
            await voice.disconnect()
            os.remove("intro.mp3")
        else:
            # queue the download.
            print('queued.')
    elif before.channel is None and after.channel is not None and member.id != 789991118443118622:
        print('Member does not have an intro in the dictionary')


# join command
@mrwelcome.command()
async def join(ctx):
    if ctx.author.voice is None:
        emoji = '❕'
        await ctx.message.add_reaction(emoji)
        await ctx.send('You must be connected to a voice '
                       'channel to use that command.')
    else:
        channel = ctx.author.voice.channel
        return await channel.connect()


# leave command
@mrwelcome.command()
async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.send('The bot is not currently '
                       'connected to a voice channel.')
    channel = ctx.author.voice.channel
    if channel is not None:
        await ctx.voice_client.disconnect()


# terminate command
@mrwelcome.command()
@commands.has_role('Developer')
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
        await ctx.send('Sorry, you do not have the necessary '
                       'role to execute this command.')
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send('Sorry, I cant run this '
                       'command from a private message!')


# Add intro
@mrwelcome.command()
async def add(ctx, url):
    # updates or adds id and url to dictionary ADT
    if is_supported(url):
        mrwelcome.d[ctx.author.id] = url
        # then update dictionary file
        with open(r"C:\Users\User\Desktop\yes\mrwelcome\Dictionary.pickle", 'wb') as handle:
            pickle.dump(mrwelcome.d, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # Adds a reaction to the message
        emoji = '👍'
        await ctx.message.add_reaction(emoji)
    else:
        await ctx.send('Invalid URL.')


# add intro error catch
@add.error
async def clear_add_intro_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('please provide a url as an argument')


# remove intro
@mrwelcome.command()
async def remove(ctx):
    if ctx.author.id not in mrwelcome.d:
        await ctx.send('There is no intro to be removed.')
    else:
        del mrwelcome.d[ctx.author.id]
        with open(r"C:\Users\User\Desktop\yes\mrwelcome\Dictionary.pickle", 'wb') as handle:
            pickle.dump(mrwelcome.d, handle, protocol=pickle.HIGHEST_PROTOCOL)
        await ctx.send('Intro successfully deleted')
        emoji = '👍'
        await ctx.message.add_reaction(emoji)


# send current intro url to chat
@mrwelcome.command()
async def current(ctx):
    if ctx.author.id in mrwelcome.d:
        await ctx.send("Your current intro is: {}".format(str(mrwelcome.d[ctx.author.id])))
    else:
        await ctx.send('You currently have no intro set.')


# voice channel meme command
@mrwelcome.command()
async def meme(ctx, arg):
    if arg in mrwelcome.meme_d:
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
        url = mrwelcome.meme_d[arg]
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            dictMeta = ydl.extract_info(url)
            duration = int(dictMeta["duration"])
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, "meme.mp3")
        ctx.voice_client.play(discord.FFmpegPCMAudio("meme.mp3"))
        time.sleep(duration+0.5)
        await ctx.voice_client.disconnect()
        os.remove("meme.mp3")
    else:
        await ctx.send('Could not find the meme you are looking for.')


@meme.error
async def clear_meme_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required argument. Did you specify the name of the meme?')


# voice channel add meme to dictionary / pickle file command
@mrwelcome.command()
async def meme_add(ctx, arg, arg_url):
    if arg not in mrwelcome.meme_d:
        if is_supported(arg_url):
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                dictMeta = ydl.extract_info(arg_url)
                duration = int(dictMeta["duration"])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file, "meme_temp.mp3")
                    os.remove('meme_temp.mp3')
            if duration < 30:
                mrwelcome.meme_d[arg] = arg_url
                with open(r"C:\Users\User\Desktop\yes\mrwelcome\meme.pickle", 'wb') as handle1:
                    pickle.dump(mrwelcome.meme_d, handle1, protocol=pickle.HIGHEST_PROTOCOL)
                emoji = '👍'
                await ctx.message.add_reaction(emoji)
            else:
                emoji = '❌'
                await ctx.message.add_reaction(emoji)
                await ctx.send('Memes must be under 30 seconds.')
        else:
            ctx.send('Invalid URL')
    else:
        await ctx.send('A meme with that name is already taken.')


@meme_add.error
async def clear_meme_add_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required argument. Did you specify the name'
                       ' and/or URL of the meme you would like to add?'
                       ' Consider using `.meme_add title url`'
                       ' where title is the name of the meme you would like to'
                       ' add and URL is the respective URL.')


# delete meme command
@mrwelcome.command()
async def meme_remove(ctx, arg):
    if arg not in mrwelcome.meme_d:
        await ctx.send('That meme does not exist.')
    else:
        del mrwelcome.meme_d[arg]
        with open(r"C:\Users\User\Desktop\yes\mrwelcome\meme.pickle", 'wb') as handle1:
            pickle.dump(mrwelcome.meme_d, handle1, protocol=pickle.HIGHEST_PROTOCOL)
        emoji = '👍'
        await ctx.message.add_reaction(emoji)


@meme_remove.error
async def clear_meme_remove_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required argument. Did you specify the name'
                       ' of the meme you would like to remove?'
                       ' Consider using `.meme_remove title`')


# list memes command
@mrwelcome.command()
async def meme_list(ctx):
    if mrwelcome.meme_d:
        memes = str(sorted(mrwelcome.meme_d.keys()))
        memes = memes.replace("[", "")
        memes = memes.replace("]", "")
        memes = memes.replace("'", "")
        await ctx.send('The current memes that can be used with'
                       ' `.meme` are:\n\n{}'.format(memes))
    else:
        await ctx.send('No memes have been added.')


# starts mrwelcome
mrwelcome.run(TOKEN)
