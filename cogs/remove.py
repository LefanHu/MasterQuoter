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
    async def remove_quote(self, ctx, quote_id: int):
        quoted_users = db.servers.find_one(
            {"_id": ctx.guild.id}, {"_id": 0, "quoted_member_ids": 1}
        )["quoted_member_ids"]

        # if no quotes saved on server
        if not quoted_users:
            await ctx.send("There are no quotes on this server")
            return

        results = db.users.update_one(
            {"_id": {"$in": quoted_users}},
            {"$pull": {"quotes": {"server_id": ctx.guild.id, "message_id": quote_id}}},
        )

        # see if anything was modified
        if results.modified_count == 0:
            await ctx.send("That quote does not exist.")
        else:
            await ctx.send("Quote removed")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(events(bot))
