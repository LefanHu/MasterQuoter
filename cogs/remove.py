from discord import Member
from discord.ext import commands
import os

from lib.db import db


class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        settings = db.servers.find_one(
            {"_id": ctx.guild.id}, {"quoted_member_ids": 0, "snips": 0}
        )
        # check if user has the masterquoter role here (if implemented)

        allowed = True
        if not settings["whitelist"] and not settings["blacklist"]:
            pass
        elif settings["whitelist"]:
            if ctx.message.author.id not in settings["allowed"]:
                allowed = False
        elif settings["blacklist"]:
            if ctx.message.author.id in settings["ignored"]:
                allowed = False

        if not allowed:
            await ctx.send("You are not allowed to manage quotes on this server.")

        return allowed

    @commands.command(aliases=["rm"], brief="Deletes a quote")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def remove(self, ctx, quote_id: int):
        """
        Deletes a saved quote/snip when given the ID.

        **Examples:**
            - mq>remove `id_here`
            - mq>rm `id_here`

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/815986506320969759/unknown.png,
        https://cdn.discordapp.com/attachments/795405783155343365/815986553537036338/unknown.png
        """
        quoted_users = db.servers.find_one(
            {"_id": ctx.guild.id}, {"_id": 0, "quoted_member_ids": 1}
        )["quoted_member_ids"]

        # if no quotes saved on server
        if not quoted_users:
            await ctx.send("There are no quotes on this server")
            return

        results = db.users.update_one(
            {"_id": {"$in": quoted_users}, "quotes.message_id": quote_id},
            {"$pull": {"quotes": {"message_id": quote_id}}},
        )

        # see if anything was modified
        if results.modified_count == 0:
            # if nothing then try removing a snip
            results = db.servers.update_one(
                {"_id": ctx.guild.id},
                {"$pull": {"snips": {"snip_id": quote_id}}},
            )
            if results.modified_count == 0:
                await ctx.send("A snip/quote by that id does not exist.")
            else:
                await ctx.send("Snippet removed.")
        else:
            await ctx.send("Quote removed")

    @commands.command(aliases=["rm_all"], brief="Removes all quotes from user")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remove_all(self, ctx, user: Member):
        """
        Removes all quotes from a specified user (ping them)

        **Examples:**
            - mq>remove_all @alex3000
            - mq>rm_all @alex3000

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/815988551866384434/unknown.png
        """
        try:  # get all quotes from that user
            quotes = db.users.find_one({"_id": user.id}, {"_id": 0, "quotes": 1})[
                "quotes"
            ]
        except TypeError:  # no quotes whatsoever
            await ctx.send(f"{0} quotes removed.")
            return

        # stripping all quotes from guild
        numRemoved = 0
        stripped_quotes = []
        for quote in quotes:
            if quote["server_id"] == ctx.guild.id:
                numRemoved += 1
                pass
            else:
                stripped_quotes.append(quote)

        # update the user's quotes
        db.users.update_one({"_id": user.id}, {"$set": {"quotes": stripped_quotes}})
        await ctx.send(f"{numRemoved} quote(s) removed.")

    # cleans up servers from database that never used the bot
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        # if no quotes and no members were saved
        server = db.servers.find_one(
            {"_id": guild.id}, {"snips": 1, "quoted_member_ids": 1}
        )

        # no snippet or quote was ever saved, so remove it
        if len(server["quoted_member_ids"]) + len(server["snips"]) == 0:
            db.servers.find_one_and_delete({"_id": guild.id})

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Remove(bot))
