import discord
from discord.ext import commands
import os


class stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(stats(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")
