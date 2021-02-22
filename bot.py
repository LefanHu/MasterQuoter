import discord
import os
from discord.ext import commands
from lib.file_utils import File
import sys

bot = commands.Bot(command_prefix=File().getenv("COMMAND_PREFIX"))
DISCORD_TOKEN = File().getenv("DISCORD_TOKEN")
DEVELOPERS = File().getenv("DEVELOPERS")
bot.ready = False

# use 135.0.54.232:27017 for accessing outside of network
mongodb = "mongodb://developer:masterbaiter@192.168.0.100:27017/masterquoter"


def is_owner(ctx):
    return ctx.message.author in DEVELOPERS


@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    return


@bot.command(hidden=True)
@commands.is_owner()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    return


@bot.command(hidden=True)
@commands.is_owner()
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} has been reloaded")
    return


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


bot.run(DISCORD_TOKEN)