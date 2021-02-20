from discord.ext import commands
import os

from discord.ext.commands.cooldowns import BucketType


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Shows the latency of this bot")
    @commands.dm_only()
    @commands.cooldown(1, 1800, BucketType.user)  # 30 mins cooldown
    async def report(self, ctx):
        """
        This command is dm_only.
        Dm this bot with this command to report an issue with this bot to the developers!

        Usage Example:
        """

        await ctx.send("Thanks! Your report has been sent to the developers")


def setup(bot):
    bot.add_cog(events(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")