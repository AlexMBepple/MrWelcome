#  File:        mrwelcome.py
#  Purpose:     Implementation of our discord welcome bot
#
#  Authors:     Ryley McRae and Alex Bepple
#  Date:        December 19, 2020

import discord
import youtube_dl
import pickle
import time
import requests
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

#get the TOKEN
tokenfile = open(r"C:\Programs\mrwelcome\very_Important.txt", "r")
TOKEN = tokenfile.readline()

#set the command prefix
mrwelcome = commands.Bot(command_prefix = '.')

#creats a bot variable of an empty dictionary(basically a global variable for bots)
mrwelcome.d = {}

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
    #reads the dictionary.pickle file and creates a dictionary ADT for the id and url pairs
    with open(r"C:\Programs\mrwelcome\Dictionary.pickle", 'rb') as handle:
        mrwelcome.d = pickle.load(handle)
    print(mrwelcome.d)

#adds mrwelcome to vc when someone joins
@mrwelcome.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None and member.id != 789991118443118622:
        channel = after.channel
        await channel.connect()

        #does something
        await self.invoke(self.mrwelcome.get_command('play'), url = mrwelcome.d[member.id])
        print('notscuffed')
        time.sleep(5)



        await member.guild.voice_client.disconnect()

########make a fucking play command for gods sake


@mrwelcome.command()
async def play(ctx, *, query):
    #Solves a problem I'll explain later
    FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    video, source = search(query)
    print(video)
    voice = get(bot.voice_clients, guild=ctx.guild)

    voice.play(FFmpegPCMAudio(source, **FFMPEG_OPTS), after=lambda e: print('done', e))
    voice.is_playing()









#join command
@mrwelcome.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    await channel.connect()

#leave command
@mrwelcome.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

#terminate command
@mrwelcome.command()
@commands.has_role("Developer")
async def terminate(ctx):
    emoji = '❌'
    await ctx.message.add_reaction(emoji)
    await mrwelcome.close()
    time.sleep(0.1) #necessary due to asyncio bug in python3.9 !!!dont remove!!!

#terminate error catch
@terminate.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        emoji = '🛑'
        await ctx.message.add_reaction(emoji)
        await ctx.send('Sorry, you do not have the necessary role to execute this command.')
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send('Sorry, I cant run this command from a private message!')

#Add intro
@mrwelcome.command()
@commands.has_permissions(manage_messages=True)
async def add_intro(ctx, url):
    if "youtu" not in url:
        await ctx.send('URL must be a valid youtube link')
    else:
        #updates or adds id and url to dictionary ADT
        mrwelcome.d[ctx.author.id] = url
        print(mrwelcome.d)
        #then update dictionary file
        with open(r"C:\Programs\mrwelcome\Dictionary.pickle", 'wb') as handle:
            pickle.dump(mrwelcome.d, handle, protocol=pickle.HIGHEST_PROTOCOL)
        #Adds a reaction to the message
        emoji = '\N{THUMBS UP SIGN}'
        # or '\U0001f44d' or '👍'
        await ctx.message.add_reaction(emoji)

#add intro error catch
@add_intro.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('please provide a url as an argument')

#starts mrwelcome
mrwelcome.run(TOKEN)
