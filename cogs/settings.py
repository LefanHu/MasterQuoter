from discord import Embed, Member
from discord.ext import commands

from typing import Optional
from datetime import datetime
from lib.db import db
import os


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        user = ctx.message.author
        if user.guild_permissions.manage_guild:
            return True

        await ctx.send(
            "You need to have 'manage_guild' permissions to change the settings of this bot."
        )
        return False

    @commands.command(brief="Changes the prefix of this bot for your server")
    async def prefix(self, ctx, *, prefix):
        if len(prefix) > 5:
            await ctx.send("Prefixes cannot be longer than 5 characters")
        else:
            db.servers.update_one({"_id": ctx.guild.id}, {"$set": {"prefix": prefix}})
            await ctx.send("Prefix set.")

    @commands.command(name="blacklist", brief="Disallows a user from saving quotes")
    async def blacklist_user(self, ctx, user: Optional[Member]):
        if not user:
            await self.toggle_blacklist(ctx)
            return
        elif type(user) != Member:
            await ctx.send("A user was not properly specified")
            return

        db.servers.update_one(
            {"_id": ctx.guild.id}, {"$addToSet": {"ignored": user.id}}
        )

    @commands.command(name="whitelist", brief="Allows a user to save quotes")
    async def whitelist_user(self, ctx, user: Optional[Member]):
        if not user:
            await self.toggle_whitelist(ctx)
            return
        elif type(user) != Member:
            await ctx.send("A user was not properly specified")
            return

        db.servers.update_one(
            {"_id": ctx.guild.id}, {"$addToSet": {"allowed": user.id}}
        )

    @commands.command(
        name="del_save_command", brief="Deletes the command after completion"
    )
    async def toggle_delete_on_save(self, ctx):
        status = db.servers.find_one({"_id": ctx.guild.id}, {"quoted_member_ids": 0})

        db.servers.find_one_and_update(
            {"_id": ctx.guild.id},
            {"$set": {"del_on_save": not status["del_on_save"]}},
            projection={"del_on_save": 1},
        )

        await ctx.send(
            f"Save commands are deleted on completion: {not status['del_on_save']}"
        )

    async def toggle_blacklist(self, ctx):
        status = db.servers.find_one({"_id": ctx.guild.id}, {"quoted_member_ids": 0})
        if status["blacklist"] != status["whitelist"]:
            if status["whitelist"] == True:
                await ctx.send(
                    "You can not have blacklist and whitelist enabled at the same time"
                )
                return

        status = db.servers.find_one_and_update(
            {"_id": ctx.guild.id},
            {"$set": {"blacklist": not status["blacklist"]}},
            projection={"blacklist": 1},
        )
        await ctx.send(f"Blacklist is now {not status['blacklist']}")

    async def toggle_whitelist(self, ctx):
        status = db.servers.find_one({"_id": ctx.guild.id}, {"quoted_member_ids": 0})
        if status["whitelist"] != status["blacklist"]:
            if status["blacklist"] == True:
                await ctx.send(
                    "You can not have blacklist and whitelist enabled at the same time"
                )
                return
        db.servers.find_one_and_update(
            {"_id": ctx.guild.id},
            {"$set": {"whitelist": not status["whitelist"]}},
            projection={"whitelist": 1},
        )
        await ctx.send(f"Whitelist is now {not status['whitelist']}")

    @commands.command(brief="unignores/pardons someone ignored on the server")
    async def pardon(self, ctx, user: Member):
        if type(user) != Member:
            await ctx.send("A user was not properly specified")
            return

        db.servers.update_one({"_id": ctx.guild.id}, {"$pull": {"ignored": user.id}})

    @commands.command(
        aliases=["settings"], brief="Shows settings of the server & stats"
    )
    async def stats(self, ctx):
        settings = db.servers.find_one({"_id": ctx.guild.id})
        guild = ctx.guild

        # Title, description, inline(boolean)
        available_settings = [
            ("Members Quoted", len(settings["quoted_member_ids"]), True),
            ("Quotes Saved", settings["quotes_saved"], True),
            ("Commands Invoked", settings["commands_invoked"], True),
            ("Server ID", guild.id, False),
            ("Bot prefix", settings["prefix"], True),
            (
                f"Delete Command On Save",
                settings["del_on_save"],
                True,
            ),
            (
                f"MasterBaiters (Blacklist Enabled: {settings['blacklist']})",
                ", ".join(
                    [(await self.bot.fetch_user(id)).name for id in settings["ignored"]]
                ),
                False,
            ),
            (
                f"MasterQuoters Users (Whitelist Enabled: {settings['whitelist']})",
                ", ".join(
                    [(await self.bot.fetch_user(id)).name for id in settings["allowed"]]
                ),
                False,
            ),
        ]

        embed = Embed(
            title=f"{guild.name}",
            description=f"{'No description' if guild.description == None else guild.description}",
            colour=ctx.message.author.colour,
            thumbnail=guild.icon_url,
            timestamp=datetime.utcnow(),
        )

        for name, value, inline in available_settings:
            embed.add_field(name=name, value=f"```{value}```", inline=inline)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Settings(bot))