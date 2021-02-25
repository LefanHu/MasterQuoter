import discord
from discord import message
from discord.ext import commands

from lib.file_utils import File
import random
from typing import Optional

from discord.ext.menus import MenuPages
from lib.quote_menu import QuoteMenu
from lib.image_menu import ImageMenu
from lib.embed_utils import embed as Emb

import pymongo

client = pymongo.MongoClient(File().getenv("DATABASE_URL"))
db = client.masterquoter


class Read(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File()

    @commands.command(aliases=["sq"], brief="Fetches a quote by ID and user")
    async def show_quote(self, ctx, message_id: int):
        """
        Fetches a specific quote when provided a quote id and user who said that quote
        Example Usage:
        """
        guild_id = ctx.guild.id
        message_id = int(message_id)

        quoted_member_ids = db.servers.find_one(
            {"_id": guild_id}, {"quoted_member_ids": 1}
        )["quoted_member_ids"]

        # No quotes
        if not quoted_member_ids:
            await ctx.send("There are no quotes saved on this server.")
            return

        quote = db.users.find_one(
            {"_id": {"$in": quoted_member_ids}},
            {
                "_id": 0,
                "quotes": {"$elemMatch": {"message_id": message_id}},
            },
        )

        if not quote:
            await ctx.send("A quote by that id does not exist")
        else:
            await self.send_quote(
                ctx, quote["quotes"][0], message=f"Quote_ID: {message_id}"
            )

    @commands.command(aliases=["qfrom"], brief="lists all quotes from user")
    async def qlist(self, ctx, user: Optional[discord.Member]):
        """Lists all quotes from a specified user"""
        if not user:
            quotes = await self.from_server(ctx.guild.id)
            if not quotes:
                await ctx.send("There are no quotes on this server")
                return
            pages = MenuPages(
                source=QuoteMenu(ctx, quotes, ctx.guild.name, ctx.guild.icon_url),
                clear_reactions_after=True,
                timeout=60.0,
            )
            await pages.start(ctx)
        else:
            quotes = await self.from_user(ctx.guild.id, user.id)
            if not quotes:
                await ctx.send("There are no quotes from this user")
                return
            pages = MenuPages(
                source=QuoteMenu(ctx, quotes, user.name, user.avatar_url),
                clear_reactions_after=True,
                timeout=60.0,
            )
            await pages.start(ctx)

    async def send_quote(self, ctx, quote, message=None, hide_user=False):
        if len(quote["image_attachments"]) <= 1:
            await ctx.send(
                message, embed=Emb().format_quote(quote, hide_user=hide_user)
            )
        else:  # deal with quotes with multiple attachments here
            quote = ImageMenu(Emb().format_quote(quote), quote["image_attachments"])
            await quote.start(ctx)

    @commands.command(aliases=["random"], brief="Gives a random saved quote")
    async def rand(self, ctx, user: Optional[discord.Member]):
        """
        This command will fetch a random quote from your server and send it if no user is specified.
        If a user is specified, this will fetch a random quote from that user.
        """

        if not user:
            quotes = await self.from_server(ctx.guild.id)
            if not quotes:
                await ctx.send("There are no quotes in this server. ")
            else:
                await self.send_quote(ctx, random.choice(quotes))
        else:  # if a user is specified
            quotes = await self.from_user(ctx.guild.id, user.id)
            if not quotes:
                await ctx.send("There are no quotes from this user on this server.")
            else:
                quote = random.choice(quotes["quotes"])
                await self.send_quote(ctx, quote)

    async def from_server(self, guild_id):
        try:
            member_ids = db.servers.find_one(
                {"_id": guild_id}, {"_id": 0, "quoted_member_ids": 1}
            )["quoted_member_ids"]

            # getting quotes from listed users in database
            cursor = db.users.find(
                {"_id": {"$in": member_ids}},
                {
                    "_id": 0,
                    "quotes": 1,
                },
            )

            # filters all quotes not from this server
            quotes = []
            quote_sections = list(cursor)
            for quote_section in quote_sections:
                for quote in quote_section["quotes"]:
                    if quote["server_id"] == guild_id:
                        quotes.append(quote)

            return quotes
        except TypeError:  # likely no server found
            return []

    async def from_user(self, guild_id, user_id):
        try:
            all_quotes = db.users.find_one({"_id": user_id}, {"_id": 0, "quotes": 1})

            quotes = []
            for quote in all_quotes["quotes"]:
                if quote["server_id"] == guild_id:
                    quotes.append(quote)

            return quotes
        except TypeError:  # likely no server found
            return []

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(File().file_name(__file__)[:-3])


def setup(bot):
    bot.add_cog(Read(bot))
