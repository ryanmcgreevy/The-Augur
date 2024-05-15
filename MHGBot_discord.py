from MHGBot import MHGBot
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')



#bot implementation
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, owner_id=414265811713130496)

mhgbot = MHGBot()

@bot.command()
@commands.is_owner()
async def sync(ctx):
    print("sync command")
    guild = discord.Object(id=420714725505105921)
    ctx.bot.tree.copy_global_to(guild=guild)
    synced = await ctx.bot.tree.sync(guild=guild)
    await ctx.send(f"Synced {len(synced)} commands to guild")

@bot.event
async def on_ready():
   #guild = discord.Object(id=420714725505105921)
   #bot.tree.copy_global_to(guild=guild)
   #await bot.tree.sync(guild=discord.Object(id=420714725505105921))
   print(f'{bot.user.name} has connected to Discord!')

@bot.tree.command(name="chat", description="Answers questions about Maxwell House Guilds.")
@app_commands.describe(message="The question or command to send the chatbot")
async def chat(interaction: discord.Interaction, message: str):
    print("invoking llm...")
    #await interaction.response.send_message(response)
    #invoking the llm takes too long at this point (beyond the 3 second slash command window)
    #need to defer and use followup instead.
    await interaction.response.defer()
    response = mhgbot.invoke_llm(message)
    await interaction.followup.send(response)

bot.run(TOKEN)


#generic client implementation
#intents = discord.Intents.default()
#intents.message_content = True
#client = discord.Client(intents=intents)
#client = discord.Client()

#@client.event
#async def on_ready():
 #   print(f'{client.user} has connected to Discord!')

#client.run(TOKEN)