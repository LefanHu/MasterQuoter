from discord.ext import commands
import os

from lib.db import db


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online.")

    @commands.command(aliases=["rm", "remove"])
    async def remove_quote(self, ctx, quote_id):
        server_id = ctx.message.guild.id

        # remove the quote here

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # remove server from the database
        quoted_member_ids = db.servers.find_one_and_delete(
            {"_id": guild.id}, {"_id": 0, "quoted_member_ids": 1}
        )["quoted_member_ids"]

        # test this
        db.users.update_many(
            {"_id": {"$in": quoted_member_ids}},
            {"quotes": {"$pull": {"quotes.server_id": guild.id}}},
        )

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(events(bot))
