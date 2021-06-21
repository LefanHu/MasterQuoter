from discord.ext import commands
from discord import TextChannel
import os, random

from asyncio import sleep
from lib.db import db


class Filter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = ["🚫", "😱", "🤬", "👺", "🐒"]

    # only if server has chat filter enabled
    async def cog_check(self, ctx):
        if db.servers.find_one({"_id": ctx.message.guild.id}, {"chat_filter": 1}):
            return True
        return False

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author != self.bot.user:
            settings = db.servers.find_one(
                {"_id": msg.guild.id},
                {"chat_filter": 1, "badwords": 1, "prefix": 1, "filtered_channels": 1},
            )
            if (
                settings["chat_filter"]
                and not msg.content.startswith(settings["prefix"])
                and msg.channel.id in settings["filtered_channels"]
            ):
                violations = 0
                used_words = []
                msg_content = msg.content.lower()
                for word in settings["badwords"]:
                    if word in msg_content:  # msg contains banned words
                        violations += 1
                        used_words.append(word)

                # deal with violation
                if violations > 0:
                    await msg.add_reaction(random.choice(self.emojis))
                    warn = await msg.channel.send(
                        f"{msg.author.mention}! {violations} violation(s): {', '.join(used_words)}\n❗ Deleting in 5 seconds."
                    )

                    await sleep(5)

                    await msg.delete()
                    await warn.delete()

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
            - mq>filter channel <channel mention>
            - mq>f rm_channel <channel mention>
            - mq>f remove <word/phrase>
            - mq>f on (turns filter on)
            - mq>f off (turns filter off)

        **Note:**
            - Will not do anything unless chat filter is enabled
            - Will not do anything unless channel is specified to be filtered

        Example Usage:
        """

        badwords = db.servers.find_one({"_id": ctx.message.guild.id}, {"badwords": 1})[
            "badwords"
        ]
        if not badwords:
            await ctx.send("There are no words to be filtered.")
        else:
            badwords = badwords[0:1900]
            await ctx.send(", ".join(badwords))

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

    @filter.command()
    async def channel(self, ctx, channel: TextChannel):
        db.servers.update_one(
            {"_id": ctx.message.guild.id},
            {"$addToSet": {"filtered_channels": channel.id}},
        )
        await ctx.send(f"{channel.mention} is now being filtered")

    @filter.command()
    async def rm_channel(self, ctx, channel: TextChannel):
        db.servers.update_one(
            {"_id": ctx.message.guild.id},
            {"$pull": {"filtered_channels": channel.id}},
        )
        await ctx.send(f"{channel.mention} is no longer being filtered")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Filter(bot))
