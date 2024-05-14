import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='chat')
async def nine_nine(ctx):
    response = ctx.message.content
    await ctx.send(response)

bot.run(TOKEN)

#intents = discord.Intents.default()
#intents.message_content = True
#client = discord.Client(intents=intents)
#client = discord.Client()

#@client.event
#async def on_ready():
 #   print(f'{client.user} has connected to Discord!')

#client.run(TOKEN)