from discord import Embed
from discord.ext import commands

from datetime import datetime
from lib.db import db
import os


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Changes the prefix of this bot for your server")
    async def prefix(self, ctx, *, prefix):
        if len(prefix) > 5:
            await ctx.send("Prefixes cannot be longer than 5 characters")
        else:
            db.servers.update_one({"_id": ctx.guild.id}, {"$set": {"prefix": prefix}})
            await ctx.send("Prefix set.")

    @commands.command(brief="Shows settings of the server & stats")
    async def settings(self, ctx):
        settings = db.servers.find_one({"_id": ctx.guild.id})

        available_settings = [
            ("Member Count", ctx.guild.member_count, True),
            ("Quotes Saved", settings["quotes_saved"], True),
            ("Commands Invoked", settings["commands_invoked"], True),
        ]

        embed = Embed(
            title="📉MasterQuoter Stats📉",
            colour=0x00FFFF,
            thumbnail=self.bot.user.avatar_url,
            timestamp=datetime.utcnow(),
        )

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Settings(bot))