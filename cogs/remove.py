from discord import Member
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

    @commands.command(aliases=["rm_all"], brief="Removes all quotes from user")
    async def remove_all(self, ctx, user: Member):
        quotes = db.users.find_one({"_id": user.id}, {"_id": 0, "quotes": 1})["quotes"]
        if not quotes:
            await ctx.send("There are no quotes from this user")

        # stripping all quotes from guild
        stripped_quotes = []
        for quote in quotes:
            if quote["server_id"] == ctx.guild.id:
                pass
            else:
                stripped_quotes.append(quote)

        db.users.update_one({"_id": user.id}, {"$set": {"quotes": stripped_quotes}})

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(events(bot))