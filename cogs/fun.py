import discord
from discord.ext import commands
import os


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def loaded_questions(self, ctx):
        await ctx.send("games ")

    @commands.command(aliases=["qGuess"])
    async def guessing_game(self, ctx):
        await ctx.send("Guess who said this quote!")


def setup(bot):
    bot.add_cog(events(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")
