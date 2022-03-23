#  Purpose:     Implementation of our discord welcome bot
#
#  Authors:     Ryley McRae and Alex Bepple
#  Date:        December 19, 2020

import discord
import youtube_dl
import pickle
import time
import youtube_dl
import os
import pprint
import math
import re
import random
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from youtube_dl import YoutubeDL
from requests import get

#Get videos from links or from youtube search
def search(query):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True'}) as ydl:
        try: requests.get(arg)
        except: info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else: info = ydl.extract_info(arg, download=False)
    return (info, info['formats'][0]['url'])

# from datetime import datetime

intents = discord.Intents.default()
intents.members = True

# get the TOKEN
tokenfile = open(r"C:\Programs\mrwelcome\very_Important.txt", "r")
TOKEN = tokenfile.readline()

# set the command prefix
mrwelcome = commands.Bot(command_prefix='.', intents=intents)

# creates a bot variable of an empty dictionary
mrwelcome.d = {}
mrwelcome.meme_d = {}

ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
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

ydl_opts= {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

#ready check and dict import
@mrwelcome.event
async def on_ready():
    print('Mr.Welcome is ready to welcome.')
    pp = pprint.PrettyPrinter(width=41, compact=True)
    # reads the dictionary.pickle file and creates a dictionary ADT for the
    # id and url pairs
    with open(r"C:\Programs\github\MrWelcome\Dictionary.pickle", "rb") as handle:
        mrwelcome.d = pickle.load(handle)
        pp.pprint(mrwelcome.d)
    with open(r"C:\Programs\github\MrWelcome\meme.pickle", 'rb') as handle1:
        mrwelcome.meme_d = pickle.load(handle1)
        pp.pprint(mrwelcome.meme_d)


# adds mrwelcome to vc when someone joins
@mrwelcome.event
async def on_voice_state_update(member, before, after):
    if member.id in mrwelcome.d and before.channel is None and after.channel is not None:
        print('{} Joined. Playing intro...'.format(member.name))
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
            dictMeta["title"] = re.sub('\W+', '', dictMeta["title"])
            print(dictMeta["title"])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file, "{}.mp3".format(dictMeta["title"]))
            voice.play(discord.FFmpegPCMAudio("{}.mp3".format(dictMeta["title"])))
            if duration > 7:
                time.sleep(7.5)  # 7500 milliseconds max
            else:
                time.sleep(duration+0.5)
            await voice.disconnect()
            time.sleep(0.1)
            os.remove("{}.mp3".format(dictMeta["title"]))
        else:
            # queue the download.
            print('queued.')
    elif before.channel is None and after.channel is not None and member.id != 789991118443118622:
        print('{} has no intro set.'.format(member.name))


# give colour event
@mrwelcome.event
async def on_raw_reaction_add(payload=discord.RawReactionActionEvent):
    if payload.channel_id == 795775258275610645:
        if str(payload.emoji).encode() == b'\xf0\x9f\x9f\xa5':
            print('red.')
            red_role = payload.member.guild.get_role(795777553432182785)
            await payload.member.add_roles(red_role)
        elif str(payload.emoji).encode() == b'\xf0\x9f\x9f\xa9':
            print('green.')
            green_role = payload.member.guild.get_role(795777697585954907)
            await payload.member.add_roles(green_role)
        elif str(payload.emoji).encode() == b'\xf0\x9f\x9f\xa6':
            print('blue.')
            blue_role = payload.member.guild.get_role(795777844151975997)
            await payload.member.add_roles(blue_role)
        elif str(payload.emoji).encode() == b'\xf0\x9f\x9f\xa7':
            print('orange.')
            orange_role = payload.member.guild.get_role(795777880016551956)
            await payload.member.add_roles(orange_role)
        elif str(payload.emoji).encode() == b'\xf0\x9f\x9f\xaa':
            print('purple.')
            purple_role = payload.member.guild.get_role(795777912540364810)
            await payload.member.add_roles(purple_role)
        elif str(payload.emoji).encode() == b'\xf0\x9f\x9f\xa8':
            print('yellow.')
            yellow_role = payload.member.guild.get_role(795778011999109170)
            await payload.member.add_roles(yellow_role)
        elif str(payload.emoji).encode() == b'\xe2\xac\x9b':
            print('black.')
            black_role = payload.member.guild.get_role(795778052276748331)
            await payload.member.add_roles(black_role)


# give colour event
@mrwelcome.event
async def on_raw_reaction_remove(payload=discord.RawReactionActionEvent):
    if payload.channel_id == 795775258275610645:
        guild = mrwelcome.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if str(payload.emoji).encode() == b'\xf0\x9f\x9f\xa5':
            print('remove red.')
            red_role = guild.get_role(795777553432182785)
            await member.remove_roles(red_role)
        elif str(payload.emoji).encode() == b'\xf0\x9f\x9f\xa9':
            print('remove green.')
            green_role = guild.get_role(795777697585954907)
            await member.remove_roles(green_role)
        elif str(payload.emoji).encode() == b'\xf0\x9f\x9f\xa6':
            print('remove blue.')
            blue_role = guild.get_role(795777844151975997)
            await member.remove_roles(blue_role)
        elif str(payload.emoji).encode() == b'\xf0\x9f\x9f\xa7':
            print('remove orange.')
            orange_role = guild.get_role(795777880016551956)
            await member.remove_roles(orange_role)
        elif str(payload.emoji).encode() == b'\xf0\x9f\x9f\xaa':
            print('remove purple.')
            purple_role = guild.get_role(795777912540364810)
            await member.remove_roles(purple_role)
        elif str(payload.emoji).encode() == b'\xf0\x9f\x9f\xa8':
            print('remove yellow.')
            yellow_role = guild.get_role(795778011999109170)
            await member.remove_roles(yellow_role)
        elif str(payload.emoji).encode() == b'\xe2\xac\x9b':
            print('remove black.')
            black_role = guild.get_role(795778052276748331)
            await member.remove_roles(black_role)


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
        await ctx.send('**Joined** `{}`'.format(channel))
        return await channel.connect()


# leave command
@mrwelcome.command()
async def leave(ctx):
    if ctx.voice_client is None:
        return await ctx.send('The bot is not currently '
                              'connected to a voice channel.')
    else:
        await ctx.voice_client.disconnect()
        await ctx.send('**Successfully disconnected**')


# terminate command
@mrwelcome.command()
@commands.has_role('Developer')
async def terminate(ctx):
    await ctx.send('**TERMINATING...**')
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.remove(file)
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
    emoji = '✅'
    await ctx.message.add_reaction(emoji)
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
        await ctx.send('I cannot run this '
                       'command from a private message!')


# Add intro
@mrwelcome.command()
async def add(ctx, url):
    # updates or adds id and url to dictionary ADT
    if url in mrwelcome.meme_d.keys():
        url = mrwelcome.meme_d[url]
    if is_supported(url):
        mrwelcome.d[ctx.author.id] = url
        # then update dictionary file
        with open(r"C:\Programs\github\MrWelcome\Dictionary.pickle", 'wb') as handle:
            pickle.dump(mrwelcome.d, handle, protocol=pickle.HIGHEST_PROTOCOL)
        # Adds a reaction to the message
        emoji = '👍'
        await ctx.message.add_reaction(emoji)
        await ctx.send('**Intro sound successfully added.**')
    else:
        await ctx.send('Invalid URL.')


# add intro error catch
@add.error
async def clear_add_intro_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required argument. Did you specify the '
                       ' URL of the intro sound you would like to add?'
                       " Consider using `.add 'url'`")


# remove intro
@mrwelcome.command()
async def remove(ctx):
    if ctx.author.id not in mrwelcome.d:
        await ctx.send('There is no intro to be removed.')
    else:
        del mrwelcome.d[ctx.author.id]
        with open(r"C:\Programs\github\MrWelcome"\Dictionary.pickle", 'wb') as handle:
            pickle.dump(mrwelcome.d, handle, protocol=pickle.HIGHEST_PROTOCOL)
        emoji = '👍'
        await ctx.message.add_reaction(emoji)
        await ctx.send('**Intro sound successfully deleted.**')


# send current intro url to chat
@mrwelcome.command()
async def current(ctx):
    if ctx.author.id in mrwelcome.d:
        await ctx.send('**Your current intro is:** {}'.format(str(mrwelcome.d[ctx.author.id])))
    else:
        await ctx.send('You currently have no intro set.')


# voice channel meme command
@mrwelcome.command()
async def meme(ctx, arg):
    if arg == "random":
        arg = random.choice(list(mrwelcome.meme_d.keys()))
    if ctx.author.voice is not None:
        if arg in mrwelcome.meme_d:
            if ctx.voice_client is None:
                await ctx.author.voice.channel.connect()
            url = mrwelcome.meme_d[arg]
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                dictMeta = ydl.extract_info(url)
            duration = int(dictMeta["duration"])
            dictMeta["title"] = re.sub('\W+', '', dictMeta["title"])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file, "{}.mp3".format(dictMeta["title"]))
            await ctx.send('**Playing meme:** `{}`'.format(arg))
            ctx.voice_client.play(discord.FFmpegPCMAudio("{}.mp3".format(dictMeta["title"])))
            print("Playing meme: {}".format(arg))
            time.sleep(duration+0.5)
            await ctx.voice_client.disconnect()
            os.remove("{}.mp3".format(dictMeta["title"]))
        else:
            await ctx.send('Could not find the meme you are looking for.')
    else:
        emoji = '❌'
        await ctx.message.add_reaction(emoji)
        await ctx.send('**You must be in a voice channel to use this command.**')


@meme.error
async def clear_meme_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required argument. Did you specify the name'
                       ' of the meme?'
                       " Consider using `.meme 'name'`")


# voice channel add meme to dictionary / pickle file command
@mrwelcome.command()
async def meme_add(ctx, arg, arg_url):
    if arg not in mrwelcome.meme_d and arg != 'random':
        if is_supported(arg_url):
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                dictMeta = ydl.extract_info(arg_url)
                duration = int(dictMeta["duration"])
            for file in os.listdir("./"):
                if file.endswith(".mp3"):
                    os.rename(file, "meme_temp.mp3")
                    os.remove('meme_temp.mp3')
            if duration < 35:
                mrwelcome.meme_d[arg] = arg_url
                with open(r"C:\Programs\github\MrWelcome\meme.pickle", 'wb') as handle1:
                    pickle.dump(mrwelcome.meme_d, handle1, protocol=pickle.HIGHEST_PROTOCOL)
                emoji = '👍'
                await ctx.message.add_reaction(emoji)
                await ctx.send('**Meme succesfully added.**')
            else:
                emoji = '❌'
                await ctx.message.add_reaction(emoji)
                await ctx.send('Memes must be under 35 seconds.')
        else:
            await ctx.send('Invalid URL')
    elif arg == 'random':
        await ctx.send("**No.**")
    else:
        await ctx.send('A meme with that name is already taken.')


@meme_add.error
async def clear_meme_add_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required argument. Did you specify the name'
                       ' and/or URL of the meme you would like to add?'
                       " Consider using `.meme_add 'name' 'url'`")


# delete meme command
@mrwelcome.command()
async def meme_remove(ctx, arg):
    if arg not in mrwelcome.meme_d:
        await ctx.send('That meme does not exist.')
    else:
        del mrwelcome.meme_d[arg]
        with open(r"C:\Programs\github\MrWelcome\meme.pickle", 'wb') as handle1:
            pickle.dump(mrwelcome.meme_d, handle1, protocol=pickle.HIGHEST_PROTOCOL)
        emoji = '👍'
        await ctx.message.add_reaction(emoji)
        await ctx.send('**Meme successfully removed.**')


@meme_remove.error
async def clear_meme_remove_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Missing required argument. Did you specify the name'
                       ' of the meme you would like to remove?'
                       " Consider using `.meme_remove 'name'`")


# list memes command
@mrwelcome.command()
async def meme_list(ctx):
    if mrwelcome.meme_d:
        memes = str(sorted(mrwelcome.meme_d.keys()))
        memes = memes.replace("[", "")
        memes = memes.replace("]", "")
        memes = memes.replace("'", "")
        await ctx.send('**The current memes that can be used with**'
                       ' `.meme` **are:**\n\n{}'.format(memes))
    else:
        await ctx.send('No memes have been added.')


# meme amount command
@mrwelcome.command()
async def meme_howmany(ctx):
    await ctx.send('**{} memes have been added.**'.format(len(mrwelcome.meme_d)))


# ping command
@mrwelcome.command()
async def ping(ctx):
    ping = mrwelcome.latency
    ping = math.floor(ping * 1000)
    await ctx.send('Pong! **{0} ms**'.format(ping, 1))


# fix command
@mrwelcome.command()
async def fix(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.remove(file)
    await ctx.send("**Fixed.**")

# starts mrwelcome
mrwelcome.run(TOKEN)
