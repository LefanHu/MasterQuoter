import discord
from discord.ext import commands
import os


class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Example(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")