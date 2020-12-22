#  File:        mrwelcome.py
#  Purpose:     Implementation of our discord welcome bot
#
#  Authors:     Ryley McRae and Alex Bepple
#  Date:        December 19, 2020

import discord
import pickle
import time
from discord.ext import commands

#get the TOKEN
tokenfile = open(r"C:\Programs\mrwelcome\very_Important.txt", "r")
TOKEN = tokenfile.readline()
# print(TOKEN)

#set the command prefix
mrwelcome = commands.Bot(command_prefix = '.')

#creats a bot variable of an empty dictionary(basically a global variable for bots)
mrwelcome.d = {}

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
        # channel.connect()
        print(member.id)
        await channel.connect()
        #does something
        print('notscuffed')
        time.sleep(5)
        await member.guild.voice_client.disconnect()

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
@mrwelcome.command(ctx)
@commands.has_role("Developer")
async def terminate():
    await mrwelcome.close()
        
#terminate error catch
@terminate.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        emoji = '🛑'
        ctx.message.add_reaction(emoji)
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



#play function

#starts mrwelcome
mrwelcome.run(TOKEN)
