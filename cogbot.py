import discord
import os
from discord.ext import commands
from cogs.file_utils import File
from menu import MyMenu

bot = commands.Bot(command_prefix=File(commands.bot).get_env("COMMAND_PREFIX"))
DISCORD_TOKEN = File(bot).get_env("DISCORD_TOKEN")


@bot.command()
async def menu_example(ctx):
    m = MyMenu()
    await m.start(ctx)


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")


@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")


@bot.command()
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} has been reloaded")


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

bot.run(DISCORD_TOKEN)