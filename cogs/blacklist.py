from discord.ext import commands
import os

from lib.db import db


class BlackList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        blacklist = db.blacklist.find_one({"_id": guild.id})
        if not blacklist:
            pass
        else:
            guild.leave()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(BlackList(bot))