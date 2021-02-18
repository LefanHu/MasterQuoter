import discord
from discord.ext import commands
import os


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def loaded_questions(self, ctx):
        # await ctx.send("games ")
        pass


def setup(bot):
    bot.add_cog(events(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")