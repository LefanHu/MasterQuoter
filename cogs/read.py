import discord
from discord.ext import commands

from lib.file_utils import File
import random
from typing import Optional

from discord.ext.menus import MenuPages
from lib.quote_menu import QuoteMenu
from lib.image_menu import ImageMenu
from lib.quote_embed import embed as Emb

import pymongo

client = pymongo.MongoClient(File().getenv("DATABASE_URL"))
db = client.masterquoter


class read(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File()

    @commands.command(aliases=["sq"], brief="Fetches a quote by ID and user")
    async def show_quote(self, ctx, user: discord.Member, message_id):
        """
        Fetches a specific quote when provided a quote id and user who said that quote
        Example Usage:
        """

        message_id = int(message_id)
        guild_id = ctx.message.guild.id

        quote = db.users.find_one(
            {"user_id": user.id},
            {
                "_id": 0,
                "quotes": {
                    "$elemMatch": {"server_id": guild_id, "message_id": message_id}
                },
            },
        )["quotes"][0]

        if not quote:
            await ctx.send("A quote by that id does not exist")
        else:
            await self.send_quote(ctx, quote, message=f"Quote_id: {message_id}")

    @commands.command(
        name="qlist", aliases=["qfrom"], brief="lists all quotes from user"
    )
    async def quotes_from(self, ctx, user: Optional[discord.Member]):
        """Lists all quotes from a specified user"""

        quotes = []

        if not user:

            # getting quoted members from server in database
            member_ids = db.servers.find_one(
                {"_id": ctx.message.guild.id}, {"_id": 0, "quoted_member_ids": 1}
            )["quoted_member_ids"]

            # getting quotes from listed users in database
            cursor = db.users.find(
                {"_id": {"$in": member_ids}},
                {
                    "_id": 0,
                    "quotes": 1,
                },
            )

            quote_sections = list(cursor)
            for quote_section in quote_sections:
                for quote in quote_section["quotes"]:
                    if quote["server_id"] == ctx.message.guild.id:
                        quotes.append(quote)
        else:
            user_quotes = db.users.find_one({"_id": user.id}, {"_id": 0, "quotes": 1})[
                "quotes"
            ]
            for quote in user_quotes:
                if quote["server_id"] == ctx.message.guild.id:
                    quotes.append(quote)

        if not quotes:
            await ctx.send(f"There are no quotes.")
            return

        pages = MenuPages(
            source=QuoteMenu(ctx, quotes), clear_reactions_after=True, timeout=60.0
        )
        await pages.start(ctx)

    async def send_quote(self, ctx, quote, message=None, hide_user=False):
        if len(quote["image_attachments"]) <= 1:
            await ctx.send(message, embed=Emb().format(quote, hide_user=hide_user))
        else:  # deal with quotes with multiple attachments here
            quote = ImageMenu(Emb.format(quote), quote["image_attachments"])
            await quote.start(ctx)

    @commands.command(name="rand", aliases=["random"])
    async def rand_from_server(self, ctx, user: Optional[discord.Member]):
        """This command will fetch a random quote from your server and send it if no user is specified.\nIf a user is specified, this will fetch a random quote from that user."""

        if not user:
            rand_user_id = random.choice(
                db.servers.find_one(
                    {"_id": ctx.message.guild.id},
                    {"_id": 0, "quoted_member_ids": 1},
                )["quoted_member_ids"]
            )
            quote = random.choice(
                db.users.find_one({"_id": rand_user_id}, {"_id": 0, "quotes": 1})[
                    "quotes"
                ]
            )

            if not quote:
                await ctx.send("There are no quotes in this server. ")
            else:
                await self.send_quote(ctx, quote)
        else:  # if a user is specified
            quote = random.choice(
                db.users.find_one({"user_id": user.id}, {"_id": 0, "quotes": 1})[
                    "quotes"
                ]
            )
            if not quote:
                await ctx.send("There are no quotes from this user on this server.")
            else:
                await self.send_quote(ctx, quote)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(File().file_name(__file__)[:-3])


def setup(bot):
    bot.add_cog(read(bot))
