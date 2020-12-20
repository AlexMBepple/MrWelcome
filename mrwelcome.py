import discord
from discord.ext import commands
TOKEN = 'Nzg5OTkxMTE4NDQzMTE4NjIy.X96Gjw.qgGaXsoKqSgwjEWUBtzq__vu0xA'
mrwelcome = commands.Bot(command_prefix = '.')


# dick = {"": ""}

@mrwelcome.event
async def on_ready():
    print('Bot is ready.')

@mrwelcome.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        channel = after.channel
        # channel.connect()
        await channel.connect()
        #does something
        print('notscuffed')
        time.sleep(5)
        await member.guild.voice_client.disconnect()

@mrwelcome.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()

@mrwelcome.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


#     play(member)
#
# play(member)



mrwelcome.run(TOKEN)
