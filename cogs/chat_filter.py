from discord.ext import commands
import os

from lib.db import db


class Filter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # only if server has chat filter enabled
    async def cog_check(self, ctx):
        if db.servers.find_one({"_id": ctx.message.guild.id}, {"chat_filter": 1}):
            return True
        return False

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author != self.bot.user:
            settings = db.servers.find_one(
                {"_id": msg.guild.id}, {"chat_filter": 1, "badwords": 1, "prefix": 1}
            )
            if settings["chat_filter"]:
                for word in settings["badwords"]:
                    if word in msg.content and not msg.content.startswith(
                        settings["prefix"]
                    ):
                        await msg.delete()

    @commands.group(
        aliases=["f"],
        invoke_without_command=True,
        brief="Commands relating to chat filtering",
    )
    async def filter(self, ctx):
        """
        Adds a word/phrase to be filtered

        **Examples:**
            - mq>filter (shows list of filtered words)
            - mq>filter add <word/phrase>

        **Note:**
            - Will not do anything unless chat filter is enabled

        Example Usage:
        """

        badwords = db.servers.find_one({"_id": ctx.message.guild.id}, {"badwords": 1})[
            "badwords"
        ]
        if not badwords:
            await ctx.send("There are no words to be filtered.")
        else:
            badwords = badwords[0:1900]
            await ctx.send(f"Here are the filtered words: {badwords}")

    @filter.command()
    async def on(self, ctx):
        db.servers.update_one(
            {"_id": ctx.message.guild.id}, {"$set": {"chat_filter": True}}
        )
        await ctx.send("Chat filter now **Enabled**")

    @filter.command()
    async def off(self, ctx):
        db.servers.update_one(
            {"_id": ctx.message.guild.id}, {"$set": {"chat_filter": False}}
        )
        await ctx.send("Chat filter now **Disabled**")

    @filter.command()
    async def add(self, ctx, *, content):
        # adds the specified content to the badwords list
        db.servers.find_one_and_update(
            {"_id": ctx.message.guild.id}, {"$addToSet": {"badwords": content}}
        )
        await self.filter(ctx)

    @filter.command()
    async def remove(self, ctx, *, content):
        db.servers.find_one_and_update(
            {"_id": ctx.message.guild.id}, {"$pull": {"badwords": content}}
        )
        await self.filter(ctx)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Filter(bot))
