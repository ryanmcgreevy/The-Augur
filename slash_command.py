from MHGBot import MHGBot
import discord
import os
from discord import app_commands

TOKEN = os.getenv('DISCORD_TOKEN')
MY_GUILD = discord.Object(id=420714725505105921)  # replace with your guild id


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')

mhgbot = MHGBot()

@client.tree.command(name="chat", description="Answers questions about Maxwell House Guilds.")
@app_commands.describe(message="The question or command to send the chatbot")
async def chat(interaction: discord.Interaction, message: str):
    print("invoking llm...")
    await interaction.response.defer()
    response = mhgbot.invoke_llm(message)
    #invoking the llm takes too long at this point (beyond the 3 second slash command window)
    #need to defer and use followup instead.
    #await interaction.response.send_message(response)
    await interaction.followup.send(response)

client.run(TOKEN)