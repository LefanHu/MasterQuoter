import discord
from discord.ext import commands
import os


class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    @commands.Cog.listener()
    async def on_ready(self):
            if not self.bot.ready:
                self.bot.cogs_ready.ready_up("help")


def setup(bot):
    bot.add_cog(Example(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")
