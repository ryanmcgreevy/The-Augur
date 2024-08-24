from augur import Augur
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
from discord.ui import Button
from discord import ButtonStyle
from discord.ext.commands import BucketType
import asyncio
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#bot implementation
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, owner_ids=[414265811713130496,301648851121471490])

augur = Augur()

@bot.command()
@commands.is_owner()
async def sync(ctx):
    # print("sync command")
    # guild = discord.Object(id=420714725505105921)
    # ctx.bot.tree.copy_global_to(guild=guild)
    synced = await ctx.bot.tree.sync()
    #synced = await ctx.bot.tree.sync(guild=guild)
    # guild = discord.Object(id=754463742246387732)
    # ctx.bot.tree.copy_global_to(guild=guild)
    # synced = await ctx.bot.tree.sync(guild=guild)
    #guild = discord.Object(id=1274425311039197345)
   # ctx.bot.tree.copy_global_to(guild=guild)
    #synced = await ctx.bot.tree.sync(guild=guild)
    await ctx.send(f"Synced {len(synced)} commands to guild")

@bot.event
async def on_ready():
   print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_guild_join(guild):
   print(f'Joined {guild.name} server!')
   bot.tree.copy_global_to(guild=guild)
   synced = await bot.tree.sync(guild=guild)
   print(f"Synced {len(synced)} commands to guild")

@bot.tree.command(name="help", description="Describes what The Augur is and how to use it.")  
async def help(interaction: discord.Interaction):
    help_text = "The Augur is an AI powered chatbot designed to answer user questions about " \
         "The Elder Scrolls Online. To use the bot, type \\chat in a " \
         "text channel and write your message to the bot. After a few seconds the bot will " \
         "respond to your question or statement."
    await interaction.response.send_message(help_text)

# @bot.tree.command(name="scrape", description="Forces The Augur to update its context sources. Owner use only.")  
# async def scrape(interaction: discord.Interaction):
#     if(await bot.is_owner(interaction.user)):
#         await interaction.response.defer()
#         augur.scrape_and_store()
#         await interaction.followup.send(ephemeral=True, content="Source data successfully scraped.")
#     else:
#         await interaction.response.send_message(ephemeral=True, content="You are not authorized to use this command.")
    

#This function returns a generator, using a generator comprehension. 
#The generator returns the string sliced, from 0 + a multiple of the length of the chunks, to the length of the chunks + a multiple of the length of the chunks.
#You can iterate over the generator like a list, tuple or string - for i in chunkstring(s,n): , or convert it into a list (for instance) with list(generator). 
#Generators are more memory efficient than lists because they generator their elements as they are needed, not all at once, however they lack certain features like indexing.
# def chunkstring(string, length):
#     return (string[0+i:length+i] for i in range(0, len(string), length))

@bot.tree.command(name="chat", description="Answers questions about The Elder Scrolls Online.")
@app_commands.describe(message="The question or command to send the chatbot")
#@discord.ext.commands.max_concurrency(number = 1, per = BucketType.user, wait=True)
async def chat(interaction: discord.Interaction, message: str):
    for entitlement in interaction.entitlements:
        if (entitlement.sku_id == 1274410251608657982 or interaction.guild_id == 754463742246387732 or interaction.guild.owner_id == 414265811713130496 ):
            break
        else:
          button = Button(style=ButtonStyle.premium, sku_id=1274410251608657982)  
          buttonview = discord.ui.View()
          buttonview.add_item(button)
          await interaction.response.send_message(content="This command is only available with a premium subscription!", 
                                                  view=buttonview)
          
    print("invoking llm...")
    #await interaction.response.send_message(response)
    #invoking the llm takes too long at this point (beyond the 3 second slash command window)
    #need to defer and use followup instead.
    await interaction.response.defer()
    try:
        await augur.invoke_llm(message, interaction)
        # for i in chunkstring(response,2000):
        #      await interaction.followup.send(i)
    except:
        await interaction.followup.send("The Augur isn't feeling well and an error has occured. Please try sending your message again")

bot.run(TOKEN)