import discord
from discord.ext import commands
import os


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online.")

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")


def setup(bot):
    bot.add_cog(events(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")