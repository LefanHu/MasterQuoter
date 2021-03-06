import discord
from discord.ext import commands

from lib.file_utils import File
import random
from typing import Optional

from discord.ext.menus import MenuPages
from lib.quote_menu import QuoteMenu
from lib.utils import Utils
from lib.quote_display import QuoteInteractionMenu
from lib.snippet_display import SnipInteractionMenu
from lib.snippet_menu import SnippetMenu

from lib.db import db


class Read(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File()
        self.utils = Utils()

    @commands.command(aliases=["sq"], brief="Fetches a quote by ID and user")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def show_quote(self, ctx, message_id: int):
        """
        Fetches a specific quote and displays it when provided a quote id.

        **Examples:**
            - mq>show_quote `quote_id_here`
            - mq>sq `quote_id_here`

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/814894523645427722/unknown.png
        """
        guild_id = ctx.guild.id

        quoted_member_ids = db.servers.find_one(
            {"_id": guild_id}, {"quoted_member_ids": 1}
        )["quoted_member_ids"]

        # No quotes
        if not quoted_member_ids:
            await ctx.send("There are no quotes saved on this server.")
            return

        quote = db.users.find_one(
            {
                "_id": {"$in": quoted_member_ids},
                "quotes.message_id": message_id,
            },
            {
                "_id": 0,
                "quotes": {"$elemMatch": {"message_id": message_id}},
            },
        )

        if not quote:
            await ctx.send("A quote by that id does not exist")
        else:
            await self.send_quote(ctx, quote["quotes"][0])

    @commands.command(aliases=["listq", "lq"], brief="lists all quotes from user")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def list_quotes(self, ctx, user: Optional[discord.Member]):
        """
        Lists all quotes from a specified user (ping them)

        **Examples:**
            - mq>list_quotes @Cuddles#2321
            - mq>listq @Cuddles#2321
            - mq>lq @Cuddles#2321

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/814655964422733844/unknown.png,
        https://cdn.discordapp.com/attachments/795405783155343365/814655522820063252/unknown.png
        """
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

    @commands.command(aliases=["lists", "ls"], brief="lists all server snippets")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def list_snips(self, ctx, user: Optional[discord.Member]):
        """
        Lists all snippets saved on the server

        **Examples:**
            - mq>list_snips
            - mq>lists
            - mq>ls

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/815949854898913340/unknown.png
        """
        snips = db.servers.find_one({"_id": ctx.guild.id}, {"snips": 1})["snips"]

        if not snips:
            await ctx.send("There are no server snippets saved.")
        else:
            pages = MenuPages(
                source=SnippetMenu(ctx, snips, ctx.guild.name, ctx.guild.icon_url),
                clear_reactions_after=True,
                timeout=60.0,
            )
            await pages.start(ctx)

    @commands.command(aliases=["ss"], brief="Shows a snippet when provided an id")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def show_snip(self, ctx, snip_id: int):
        """
        Shows a snippet when provided an id. You can see the id of a quote/snip when it is saved, or you can find it through `lists` or `listq`.

        **Examples:**
            - mq>show_snip `snippet_id`
            - mq>ss `snippet_id`

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/816035755952439296/unknown.png
        """
        try:
            snip = db.servers.find_one(
                {"_id": ctx.guild.id}, {"snips": {"$elemMatch": {"snip_id": snip_id}}}
            )["snips"][0]
        except KeyError:
            await ctx.send("A snippet by that id does not exist.")
            return

        descriptions = self.utils.split_snip(snip)
        if len(descriptions) + len(snip["images"]) > 2:
            snip = SnipInteractionMenu(snip)
            await snip.start(ctx)
        else:
            embed = self.utils.format_snip(snip)
            await ctx.send(embed=embed)

    async def send_quote(self, ctx, quote, message=None, hide_user=False):
        quote_length = len(" ".join(quote["msg"]))
        image_count = len(quote["image_attachments"])

        if image_count > 1 or quote_length > 2000:
            quote = QuoteInteractionMenu(quote, hide_user=hide_user)
            await quote.start(ctx)
        else:  # instead of sending as a interaction menu, sends normally as embed
            await ctx.send(
                message, embed=self.utils.format_quote(quote, hide_user=hide_user)
            )

    @commands.command(aliases=["rand"], brief="Gives a random saved quote")
    @commands.cooldown(1, 2, commands.BucketType.user)  # change this to 5 later
    async def random(self, ctx, user: Optional[discord.Member]):
        """
        This command will fetch a random quote from your server and send it if __no user is specified__.

        If a __user is specified__, this will fetch a random quote from that user.

        **Examples:**
            - mq>random
            - mq>rand
            - mq>rand @alex3000

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/814983175100039234/unknown.png
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
                quote = random.choice(quotes)
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
            self.bot.cogs_ready.ready_up(self.file.file_name(__file__)[:-3])


def setup(bot):
    bot.add_cog(Read(bot))
