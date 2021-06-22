import discord
from discord.ext import commands, tasks
from time import time
import os


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Shows full size of user's profile pic")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def pfp(self, ctx, user: discord.Member):
        """
        This shows the full size of another user's profile picture.

        **Example:**
            - mq>pfp <@mention>

        Example Usage:
        """
        await ctx.send(user.avatar_url)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Basic(bot))
