from discord.ext import commands
from lib.db import db
import os


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Changes the prefix of this bot for your server")
    async def prefix(self, ctx, *, prefix):
        if len(prefix) > 5:
            await ctx.send("prefixes cannot be longer than 5 characters")
        else:
            db.servers.find({"_id": ctx.guild.id}, {"$set": {"prefix": prefix}})

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Settings(bot))