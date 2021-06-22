from discord.ext import commands
from discord import TextChannel, Member, Embed
import os, random

from asyncio import sleep
from lib.db import db


class Filter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojis = ["🚫", "😱", "🤬", "👺", "🐒"]

    # only if server has chat filter enabled
    async def cog_check(self, ctx):
        if db.filters.find_one({"_id": ctx.message.guild.id}, {"enabled": 1}):
            return True
        return False

    # adds empty filter for new servers
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        new_filter = {
            "_id": guild.id,
            "name": guild.name,
            "prefix": db.servers.find_one({"_id": guild.id}, {"prefix": 1})["prefix"],
            "mode": 0,
            "enabled": False,
            "filtered_channels": [],
            "filtered_users": [],
            "badwords": [],
            "violations": {},
        }
        db.filters.insertOne(new_filter)

    # adds new guild if there isn't one
    async def new_filter(self, guild):
        new_filter = {
            "_id": guild.id,
            "name": guild.name,
            "prefix": db.servers.find_one({"_id": guild.id}, {"prefix": 1})["prefix"],
            "mode": 0,
            "enabled": False,
            "filtered_channels": [],
            "filtered_users": [],
            "badwords": [],
            "violations": {},
        }
        db.filters.insert_one(new_filter)

    async def update_violations(self, msg, violations: int):
        count = db.filters.find_one_and_update(
            {"_id": msg.guild.id},
            {"$inc": {f"violations.{msg.author.id}": 1}},
            {"violations": 1},
            upsert=True,
        )

        try:
            num = count["violations"][str(msg.author.id)]
            return num + 1
        except KeyError:
            return 1

    @commands.Cog.listener()
    async def on_message(self, msg):
        settings = db.filters.find_one({"_id": msg.guild.id})
        if not settings:
            await self.new_filter(msg.guild)

        # if filter is enabled and message author is not self
        if (
            not msg.author.bot
            and settings["enabled"]
            and not msg.content.startswith(settings["prefix"])
        ):
            violations = 0
            badwords = []
            msg_content = msg.content.lower()

            if settings["mode"] > 0:  # filters all messages in guild
                for word in settings["badwords"]:
                    if word in msg_content:  # msg contains banned words
                        violations += 1
                        badwords.append(word)
            elif settings["mode"] < 0:  # filters all messages from specified user
                if msg.author.id in settings["filtered_users"]:
                    for word in settings["badwords"]:
                        if word in msg_content:  # msg contains banned words
                            violations += 1
                            badwords.append(word)
            else:  # filters all messages for specified channel
                if msg.channel.id in settings["filtered_channels"]:
                    for word in settings["badwords"]:
                        if word in msg_content:  # msg contains banned words
                            violations += 1
                            badwords.append(word)

            # deal with violation
            if violations > 0:
                # updates violation count
                num_violations = await self.update_violations(msg, violations)

                # identifies words that contains badwords
                used_words = []
                words = msg.content.split(" ")
                for badword in badwords:
                    index = msg.content.find(badword)
                    chars = 0
                    for word in words:
                        chars += len(word)
                        if chars >= index:
                            used_words.append(word)
                            break

                await msg.add_reaction(random.choice(self.emojis))
                warn = await msg.channel.send(
                    f"{msg.author.mention}! This is your **#{num_violations} violation**!\n{violations} violation(s): **{', '.join(used_words)}** contains {', '.join(badwords)}❗\n Deleting in 5 seconds❗"
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
            - mq>f remove <word/phrase>
            - mq>f mode <user/channel/guild>
            - mq>f channel <channel mention>
            - mq>f rm_channel <channel mention>
            - mq>f user
            - mq>f on (turns filter on)
            - mq>f off (turns filter off)

        **Note:**
            - Will not do anything unless chat filter is enabled
            - Mode is set to channel by default, specify a channel to be filtered

        Example Usage:
        """

        badwords = db.filters.find_one({"_id": ctx.message.guild.id}, {"badwords": 1})[
            "badwords"
        ]
        if not badwords:
            await ctx.send("There are no words to be filtered.")
        else:
            badwords = badwords[0:1900]
            await ctx.send(f"Filtered words: **{', '.join(badwords)}**")

    @filter.command()
    async def mode(self, ctx, scope):
        if scope == "channel":
            db.filters.update_one({"_id": ctx.message.guild.id}, {"$set": {"mode": 0}})
        elif scope == "user":
            db.filters.update_one({"_id": ctx.message.guild.id}, {"$set": {"mode": -1}})
        elif scope == "guild":
            db.filters.update_one({"_id": ctx.message.guild.id}, {"$set": {"mode": 1}})
        else:
            await ctx.send("Your only options are 'channel', 'guild', and 'user'!")
            return

        await ctx.send(f"{scope} is now being filtered")

    @filter.command()
    async def on(self, ctx):
        db.filters.update_one(
            {"_id": ctx.message.guild.id}, {"$set": {"enabled": True}}
        )
        await ctx.send("Chat filter now **Enabled**")

    @filter.command()
    async def off(self, ctx):
        db.filters.update_one(
            {"_id": ctx.message.guild.id}, {"$set": {"enabled": False}}
        )
        await ctx.send("Chat filter now **Disabled**")

    @filter.command()
    async def add(self, ctx, *, content):
        # adds the specified content to the badwords list
        db.filters.update_one(
            {"_id": ctx.message.guild.id}, {"$addToSet": {"badwords": content}}
        )
        await self.filter(ctx)

    @filter.command()
    async def remove(self, ctx, *, content):
        db.filters.update_one(
            {"_id": ctx.message.guild.id}, {"$pull": {"badwords": content}}
        )
        await self.filter(ctx)

    @filter.command()
    async def user(self, ctx, member: Member):
        db.filters.update_one(
            {"_id": ctx.message.guild.id}, {"$addToSet": {"filtered_users": member.id}}
        )
        await ctx.send(f"{member.display_name}'s messages are **now** being filtered")

    @filter.command()
    async def rm_user(self, ctx, member: Member):
        db.filters.update_one(
            {"_id": ctx.message.guild.id}, {"$addToSet": {"filtered_users": member.id}}
        )
        await ctx.send(
            f"{member.display_name}'s messages are **no longer** being filtered"
        )

    @filter.command()
    async def channel(self, ctx, channel: TextChannel):
        db.filters.update_one(
            {"_id": ctx.message.guild.id},
            {"$addToSet": {"filtered_channels": channel.id}},
        )
        await ctx.send(f"{channel.mention} is now being filtered")

    @filter.command()
    async def rm_channel(self, ctx, channel: TextChannel):
        db.filters.update_one(
            {"_id": ctx.message.guild.id},
            {"$pull": {"filtered_channels": channel.id}},
        )
        await ctx.send(f"{channel.mention} is no longer being filtered")

    @filter.command(aliases=["s"])
    async def settings(self, ctx):
        filter = db.filters.find_one({"_id": ctx.message.guild.id})
        guild = ctx.message.guild

        embed = Embed(title="📉 Server Filter Settings 📉", colour=0x00FFFF)

        if filter["mode"] > 0:
            mode = "guild"
        elif filter["mode"] < 0:
            mode = "user"
        else:
            mode = "channel"

        fields = [
            ("Filter Mode", mode, True),
            ("Filter Status", filter["enabled"], True),
            (
                "Filtered Channels",
                ", ".join(
                    [
                        channel.name
                        for channel in guild.channels
                        if channel.id in filter["filtered_channels"]
                    ]
                )
                if filter["filtered_channels"]
                else " ",
                False,
            ),
            (
                "Filtered Users",
                ", ".join(
                    [
                        user.name
                        for user in guild.members
                        if user.id in filter["filtered_users"]
                    ]
                )
                if filter["filtered_users"]
                else " ",
                False,
            ),
            (
                "Banned Words",
                ", ".join(filter["badwords"]) if filter["badwords"] else " ",
                False,
            ),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=f"```{value}```", inline=inline)

        await ctx.send(embed=embed)

    # @filter.command()
    # async def top_score(self, ctx):
    #     violations = db.filters.find_one(
    #         {"_id": ctx.message.guild.id}, {"violations": 1}
    #     )
    #     try:
    #         scores = violations["violations"]
    #         await ctx.send(scores)
    #     except KeyError:
    #         await ctx.send("There are no violations yet!")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Filter(bot))
