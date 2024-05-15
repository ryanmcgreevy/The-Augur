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

@bot.tree.command(name="chat", description="Answers questions about Maxwell House Guilds.")
@app_commands.describe(message="The question or command to send the chatbot")
async def chat(interaction: discord.Interaction, message: str) -> None:
    print("invoking llm...")
    await interaction.response.send_message(mhgbot.invoke_llm(message))

@bot.command()
@commands.is_owner()
async def sync(ctx):
    print("sync command")
    guild = discord.Object(id=420714725505105921)
    ctx.bot.tree.copy_global_to(guild=guild)
    synced = await ctx.bot.tree.sync(guild=guild)
    await ctx.send(f"Synced {len(synced)} commands globally")

@bot.event
async def on_ready():
   await bot.tree.sync(guild=discord.Object(id=420714725505105921))
   print(await bot.tree.fetch_commands())
   print(bot.tree.get_commands()[0].name)
   print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='mhg', help="Answers questions about Maxwell House Guilds")
async def mhg(ctx):
   user_input = ctx.message.content[4:]
   response = mhgbot.invoke_llm(user_input)
   await ctx.send(response)

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