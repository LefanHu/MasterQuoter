import discord
from discord.ext import commands

from lib.file_utils import File
import os
import random
from typing import Optional

from discord.ext.menus import MenuPages
from lib.quote_menu import QuoteMenu
from lib.image_menu import ImageMenu
from lib.quote_embed import embed as Emb

from bot import DEVELOPERS


class read(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File()
        self.save_location = self.file.getenv("SAVE_LOCATION")
        self.quotes_per_page = 10

    def is_owner(self, ctx):
        return ctx.message.author in DEVELOPERS

    @commands.command(aliases=["s"], brief="Fetches a quote by ID")
    async def show(self, ctx, quote_id):
        """Fetches a specific quote when provided a quote id"""
        quote = self.file.fetch_quote(ctx.message.guild.id, int(quote_id))
        if not quote:
            await ctx.send("A quote by that id does not exist")
        else:
            await self.send_quote(ctx, quote, message=f"Quote: {quote_id}")

    @commands.command(
        name="qlist", aliases=["qfrom"], brief="lists all quotes from user"
    )
    async def quotes_from_member(self, ctx, user: Optional[discord.Member]):
        """Lists all quotes from a specified user"""
        if not user:
            quotes = self.file.from_server(ctx.message.guild.id)
        else:
            quotes = self.file.from_user(user.id, ctx.message.guild.id)

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
            quote = ImageMenu(quote, message)
            await quote.start(ctx)

    @commands.command(name="rand", aliases=["random"])
    async def rand_from_server(self, ctx, user: Optional[discord.Member]):
        """This command will fetch a random quote from your server and send it if no user is specified.\nIf a user is specified, this will fetch a random quote from that user."""
        quotes = self.file.from_server(ctx.message.guild.id)

        if not user:
            if not quotes:
                await ctx.send("There are no quotes in this server. ")
            else:
                quote = random.choice(quotes)
                await self.send_quote(ctx, quote)
        else:  # if a user is specified
            quotes = self.file.from_user(user.id, ctx.message.guild.id)
            if not quotes:
                await ctx.send("There are no quotes from this user on this server.")
            else:
                quote = random.choice(quotes)
                await self.send_quote(ctx, quote)


def setup(bot):
    bot.add_cog(read(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")
