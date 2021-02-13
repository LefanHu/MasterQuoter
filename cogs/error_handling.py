import discord
from discord.ext import commands
import os


class error_handle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please pass in all required arguments.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You're missing the required permissions")


def setup(bot):
    bot.add_cog(error_handle(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")