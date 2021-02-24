from discord import Embed, Member
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

    @commands.command(brief="Makes the bot ignore a user")
    async def ignore(self, ctx, user: Member):
        if type(user) != Member:
            await ctx.send("A user was not properly specified")
            return

        db.servers.update_one(
            {"_id": ctx.guild.id}, {"$addToSet": {"ignored": user.id}}
        )

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
                "Users to ignore",
                ", ".join([self.bot.get_user(id).name for id in settings["ignored"]]),
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