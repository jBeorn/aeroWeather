import discord
from discord.ext import commands
from discord import app_commands
import time

from settings import TOKEN, OWNER_ID, PREFIX


class Client(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        # intents.members = True
        super().__init__(command_prefix = commands.when_mentioned_or(PREFIX), intents = intents, help_command = None)
        self.gears = ["cogs.aeroWeather"]


    async def setup_hook(self):
        for ext in self.gears:
            await self.load_extension(ext)


    async def on_ready(self):
        print(f' We have logged in as {client.user}')
        print(time.strftime(" %H:%M:%S UTC ", time.gmtime()))
        print(" Discord.py version - ", discord.__version__)


client = Client()


@client.command()
async def sync(ctx):
    print("syncing slash commands")
    if ctx.author.id == OWNER_ID:
        synced = await client.tree.sync()
        print(f" {len(synced)} Slash Command's Synced ")
    else:
        print(ctx.author.name, "has no permission")


@client.hybrid_command()
async def ping(ctx: commands.Context):
    await ctx.send(f"``Pong! {round(client.latency * 1000)}ms``  📡")


client.run(TOKEN)