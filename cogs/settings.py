from discord import Embed, Member
from discord.ext import commands

from typing import Optional
from datetime import datetime
from lib.db import db
from os.path import basename


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_commands = ["stats", "settings"]

    async def cog_check(self, ctx):
        user = ctx.message.author
        if user.guild_permissions.manage_guild:
            return True
        elif ctx.command.name in self.allowed_commands:
            return True
        await ctx.send(
            "You need to have `manage_guild` permissions to change the settings of this bot."
        )
        return False

    @commands.command(brief="Changes the prefix of this bot for your server")
    async def prefix(self, ctx, *, prefix):
        """
        This command will change the prefix for this bot on your server.

        **Example:**
            - mq>prefix .

        **Note:**
            - Prefix cannot be set to anything longer than 5 characters
            - `manage server` permissions are required

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/814984460536774686/unknown.png
        """
        if len(prefix) > 5:
            await ctx.send("Prefixes cannot be longer than 5 characters")
        else:
            db.servers.update_one({"_id": ctx.guild.id}, {"$set": {"prefix": prefix}})
            await ctx.send("Prefix set.")

    @commands.command(name="blacklist", brief="Disallows a user from saving quotes")
    @commands.has_guild_permissions(manage_guild=True)
    async def blacklist_user(self, ctx, user: Optional[Member]):
        """
        Command will toggle on and off blacklist if a user is not specified. If a user is specified, that user will be added to the blacklist.

        Blacklisted people are **NOT ALLOWED** to manage quotes:
            - `remove`, `rm_all`, `snip`, `quote`, `qlast`

        **Example:**
            - mq>blacklist <= Toggles on & off blacklist
            - mq>blacklist @alex3000

        **Note:**
            - Blacklist does nothing unless it is **ENABLED**
            - You can not have whitelist **AND** blacklist enabled

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/815983496014856196/unknown.png
        """
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
        """
        Command will toggle on and off whitelist if a user is not specified. If a user is specified, that user will be added to the whitelist.

        Whitelisted people are **ALLOWED** to manage quotes:
            - `remove`, `rm_all`, `snip`, `quote`, `qlast`

        **Example:**
            - mq>whitelist <= Toggles on & off whitelist
            - mq>whitelist @alex3000

        **Note:**
            - Whitelist does nothing unless it is **ENABLED**
            - You can not have whitelist **AND** blacklist enabled

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/815984194580774922/unknown.png
        """
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
        name="delete_save_command", brief="Deletes the command after completion"
    )
    async def toggle_delete_on_save(self, ctx):
        """
        This command toggles whether or not commands that saved a quote will be deleted after completion.

        **Example:**
            - mq>delete_save_command

        **Note:**
            - Commands that saves an image along with it will **NOT** be deleted this is because image urls will be come __invalid__ after the message is deleted.

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/814986325249490944/unknown.png,
        https://cdn.discordapp.com/attachments/795405783155343365/814986401182384168/unknown.png
        """
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

    @commands.command(brief="Remove a user from the blacklist")
    async def pardon(self, ctx, user: Member):
        """
        This removes someone from the blacklist. See help `blacklist`, for what it does.

        **Example:**
            - mq>pardon @alex3000

        **Note:**
            - Blacklist does nothing if it is not __enabled__

        Example Usage:
        """
        if type(user) != Member:
            await ctx.send("A user was not properly specified")
            return

        db.servers.update_one({"_id": ctx.guild.id}, {"$pull": {"ignored": user.id}})

    @commands.command(brief="Remove a user from the whitelist")
    async def restrict(self, ctx, user: Member):
        """
        This removes someone from the whitelist. See help `whitelist`, for what it does.

        **Example:**
            - mq>restrict @alex3000

        **Note:**
            - Whitelist does nothing if it is not __enabled__

        Example Usage:
        """
        if type(user) != Member:
            await ctx.send("A user was not properly specified")
            return

        db.servers.update_one({"_id": ctx.guild.id}, {"$pull": {"allowed": user.id}})

    @commands.command(aliases=["stats"], brief="Shows settings of the server & stats")
    async def settings(self, ctx):
        """
        Displays your server settings. This includes:
        - bot prefix for your server
        - total quotes saved
        - commands invoked
        - server id
        - delete command on server (Enabled/Disabled)
        - blacklist
        - whitelist

        **Example:**
            - mq>settings

        Example Usage:
        """
        settings = db.servers.find_one({"_id": ctx.guild.id})
        guild = ctx.guild

        # Title, description, inline(boolean)
        available_settings = [
            ("😆Quotes Saved😆", settings["quotes_saved"], True),
            ("😤Commands Invoked😤", settings["commands_invoked"], True),
            ("🎛️Bot prefix🎛️", settings["prefix"], True),
            ("🛡️Server ID🛡️", guild.id, True),
            (
                f"❌Delete Command On Save",
                settings["del_on_save"],
                False,
            ),
            (
                f"📝Quoted Members: {len(settings['quoted_member_ids'])}",
                ", ".join(
                    [
                        (await self.bot.fetch_user(id)).name
                        for id in settings["quoted_member_ids"]
                    ]
                )
                + " ",
                False,
            ),
            (
                f"🏴 MasterBaiters (Blacklist Enabled: __{settings['blacklist']}__)",
                ", ".join(
                    [(await self.bot.fetch_user(id)).name for id in settings["ignored"]]
                )
                + " ",
                False,
            ),
            (
                f"🏳️ MasterQuoters (Whitelist Enabled: __{settings['whitelist']}__)",
                ", ".join(
                    [(await self.bot.fetch_user(id)).name for id in settings["allowed"]]
                )
                + " ",
                False,
            ),
            ("⁉️**BUGS & ERRORS**", "TO FILE A REPORT, DM THE MASTERQUOTER BOT", False),
        ]

        embed = Embed(
            title=f"⚙️ {guild.name} Stats/Settings⚙️",
            description=f"{'No server description' if guild.description == None else guild.description}",
            colour=ctx.message.author.colour,
            timestamp=datetime.utcnow(),
        )
        embed.set_thumbnail(url=guild.icon_url)

        for name, value, inline in available_settings:
            embed.add_field(name=name, value=f"```{value}```", inline=inline)

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Settings(bot))
