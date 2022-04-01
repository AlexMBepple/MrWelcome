#       "Mr Welcome" written using discord.py API
#       Ryley McRae and Alex Bepple
#       Newest additions:  March 31, 2022

import discord
import pickle
import asyncio
import time
import youtube_dl
import sys
import os
import pprint
import math
import random

from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

# get the TOKEN
tokenfile = open(os.path.join(sys.path[0], "very_Important.txt"), "r")
TOKEN = tokenfile.readline()

# set the command prefix
bot = commands.Bot(command_prefix='.', intents=intents, help_command=commands.DefaultHelpCommand())

# creates a bot variable of an empty dictionary
bot.d = {}
bot.meme_d = {}
bot.song_q = []     # song queue

def botdisconnect(vc):
    bot.song_q.clear()
    asyncio.run_coroutine_threadsafe(vc.disconnect(), bot.loop)

def play_next(ctx):
    # time.sleep(1)
    vc = ctx.voice_client
    del bot.song_q[0]
    if len(bot.song_q) >= 1:
        url = bot.song_q[0]
        player = asyncio.run_coroutine_threadsafe(YTDLSource.from_url(url, loop=bot.loop, stream=True), bot.loop)
        vc.play(player.result(), after=lambda e: play_next(ctx))
    else:
        asyncio.run_coroutine_threadsafe(vc.disconnect(), bot.loop)

class CustomHelp(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        for cog in mapping:
            await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in mapping[cog]]}')
        # return await super().send_bot_help(mapping)

    async def send_cog_help(self, cog):
        await self.get_destination().send(f'{cog.qualified_name}: {[command.name for command in cog.get_commands()]}')
        # return await super().send_cog_help(cog)

    async def send_group_help(self, group):
        await self.get_destination().send(f'{group.name}: {[command.name for index , command in enumerate(group.commands)]}')
        # return await super().send_group_help(group)

    async def send_command_help(self, command):
        await self.get_destination().send(command.name)
        # return await super().send_command_help(command)


# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
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
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


def is_supported(url):
    extractors = youtube_dl.extractor.gen_extractors()
    for e in extractors:
        if e.suitable(url) and e.IE_NAME != 'generic':
            return True
    return False


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['summon', 'connect'])
    async def join(self, ctx):
        """Joins a voice channel"""
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command(aliases=['leave', 'die'])
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        if ctx.author.voice is None:
            return await ctx.send("You must be connected to a voice channel to use that command.")
        if ctx.voice_client:
            bot.song_q.clear()
            await ctx.voice_client.disconnect()

    @commands.command()
    async def meme(self, ctx, *, arg):
        """Plays a meme from the meme dictionary"""
        if arg == "random":
            arg = random.choice(list(bot.meme_d.keys()))
        url = bot.meme_d[arg]
        bot.song_q.append(url)
        if ctx.voice_client.is_playing():
            await ctx.send('**Meme:** `{}` has been queued in spot {}.'.format(arg,len(bot.song_q)))
        else:
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                try:
                    ctx.voice_client.play(player, after=lambda e: play_next(ctx))
                    await ctx.send(f'**Playing meme:** `{arg}`')
                except:
                    await ctx.send(f'The meme `{arg}` is no longer available')

    @join.before_invoke
    @meme.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You must be connected to a voice channel to use that command.")
            raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client is None:
            await ctx.author.voice.channel.connect()

    @meme.error
    async def clear_meme_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing required argument. Did you specify the name'
                           ' of the meme?'
                           " Consider using `.meme 'name'`")
        if isinstance(error, commands.CommandError):
            print(error)


class Generic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # closes the bot
    @commands.command()
    @commands.has_role('Developer')
    async def terminate(self, ctx):
        """Turns off the bot (Developer role required)"""
        await ctx.send('**TERMINATING...**')
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
        emoji = '✅'
        await ctx.message.add_reaction(emoji)
        await bot.close()
        time.sleep(0.1)  # necessary due to asyncio bug in python3.9

    # terminate error catch
    @terminate.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRole):
            emoji = '🛑'
            await ctx.message.add_reaction(emoji)
            await ctx.send('Sorry, you do not have the necessary '
                           'role to execute this command.')
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send('I cannot run this '
                           'command from a private message!')

    # add intro to dictionary
    @commands.command()
    async def add(self, ctx, url):
        """Use this to add/update your intro song"""
        # updates or adds id and url to dictionary ADT
        if url in bot.meme_d.keys():
            url = bot.meme_d[url]
        if is_supported(url):
            bot.d[ctx.author.id] = url
            # then update dictionary file
            with open(os.path.join(sys.path[0], "Dictionary.pickle"), 'wb') as handle:
                pickle.dump(bot.d, handle, protocol=pickle.HIGHEST_PROTOCOL)
            # Adds a reaction to the message
            emoji = '👍'
            await ctx.message.add_reaction(emoji)
            await ctx.send('**Intro sound successfully added.**')
        else:
            await ctx.send('Invalid URL.')

    # add intro error catch
    @add.error
    async def clear_add_intro_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing required argument. Did you specify the '
                           ' URL of the intro sound you would like to add?'
                           " Consider using `.add 'url'`")

    # remove intro
    @commands.command()
    async def remove(self, ctx):
        """Use this to remove your current intro song"""
        if ctx.author.id not in bot.d:
            await ctx.send('There is no intro to be removed.')
        else:
            del bot.d[ctx.author.id]
            with open(os.path.join(sys.path[0], "Dictionary.pickle"), 'wb') as handle:
                pickle.dump(bot.d, handle, protocol=pickle.HIGHEST_PROTOCOL)
            emoji = '👍'
            await ctx.message.add_reaction(emoji)
            await ctx.send('**Intro sound successfully deleted.**')

    # send current intro url to chat
    @commands.command()
    async def current(self, ctx):
        """Displays your current intro song"""
        if ctx.author.id in bot.d:
            await ctx.send('**Your current intro is:** {}'.format(str(bot.d[ctx.author.id])))
        else:
            await ctx.send('You currently have no intro set.')

    # voice channel add meme to dictionary / pickle file command
    @commands.command()
    async def meme_add(self, ctx, arg, arg_url):
        """Adds a meme to meme dictionary"""
        if arg not in bot.meme_d and arg != 'random':
            if is_supported(arg_url):
                data = ytdl.extract_info(arg_url)
                if int(data["duration"]) < 35:
                    bot.meme_d[arg] = arg_url
                    with open(os.path.join(sys.path[0], "meme.pickle"), 'wb') as handle1:
                        pickle.dump(bot.meme_d, handle1, protocol=pickle.HIGHEST_PROTOCOL)
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
    async def clear_meme_add_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing required argument. Did you specify the name'
                           ' and/or URL of the meme you would like to add?'
                           " Consider using `.meme_add 'name' 'url'`")

    # delete meme command
    @commands.command()
    async def meme_remove(self, ctx, arg):
        """Removes the specific meme from meme dictionary"""
        if arg not in bot.meme_d:
            await ctx.send('That meme does not exist.')
        else:
            del bot.meme_d[arg]
            with open(os.path.join(sys.path[0], "meme.pickle"), 'wb') as handle1:
                pickle.dump(bot.meme_d, handle1, protocol=pickle.HIGHEST_PROTOCOL)
            emoji = '👍'
            await ctx.message.add_reaction(emoji)
            await ctx.send('**Meme successfully removed.**')

    @meme_remove.error
    async def clear_meme_remove_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Missing required argument. Did you specify the name'
                           ' of the meme you would like to remove?'
                           " Consider using `.meme_remove 'name'`")

    # list memes command
    @commands.command()
    async def meme_list(self, ctx):
        """Lists all memes in the meme dictionary"""
        if bot.meme_d:
            memes = str(sorted(bot.meme_d.keys()))
            memes = memes.replace("[", "")
            memes = memes.replace("]", "")
            memes = memes.replace("'", "")
            await ctx.send('**The current memes that can be used with**'
                           ' `.meme` **are:**\n\n{}'.format(memes))
        else:
            await ctx.send('No memes have been added.')

    # Number of memes command
    @commands.command()
    async def meme_howmany(self, ctx):
        """Displays how many memes have been added"""
        await ctx.send('**{} memes have been added.**'.format(len(bot.meme_d)))

    # ping command
    @commands.command()
    async def ping(self, ctx):
        """Displays the bots current latency"""
        ping = bot.latency
        ping = math.floor(ping * 1000)
        await ctx.send(f'Pong! **{0} ms**'.format(ping, 1))

    # fix command
    @commands.command()
    async def fix(self, ctx):
        """deletes any mp3 files in the bot's working directory and disconnects it from voice"""
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.remove(file)
        await ctx.send("**Fixed.**")


@bot.event
async def on_voice_state_update(member, before, after):
    """Bot joins if member connects from None and has a set intro"""
    if member.id in bot.d and before.channel is None:
        print('{} Joined. Playing intro...'.format(member.name))
        vs = member.guild.me.voice
        url = bot.d[member.id]
        if not vs:
            await after.channel.connect()
        else:
            try:
                await member.guild.voice_client.move_to(after.channel)
            except:
                print('could not move_to')
        vc = member.guild.voice_client
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        vc.play(player, after=lambda e: botdisconnect(vc))
    elif before.channel is None and member.id != 789991118443118622:    # filter out event for member.id == bot's ID
        print('{} has no intro set.'.format(member.name))


# ready check and dict import
@bot.event
async def on_ready():
    print('Mr.Welcome is ready to welcome.')
    pp = pprint.PrettyPrinter(width=41, compact=True)
    # reads the dictionary.pickle file and creates a dictionary ADT for the
    # id and url pairs
    with open(os.path.join(sys.path[0], "Dictionary.pickle"), "rb") as handle:
        bot.d = pickle.load(handle)
        pp.pprint(bot.d)
    with open(os.path.join(sys.path[0], "meme.pickle"), "rb") as handle1:
        bot.meme_d = pickle.load(handle1)
        pp.pprint(bot.meme_d)


bot.add_cog(Generic(bot))
bot.add_cog(Voice(bot))
bot.run(TOKEN)
