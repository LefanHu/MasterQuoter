import discord
from discord.ext import commands

from lib.file_utils import File
import os
import random

from discord.ext.menus import MenuPages
from lib.quote_menu import QuoteMenu
from lib.attachment_menu import AttachmentMenu
from lib.quote_embed import embed as Emb


class read(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File()
        self.save_location = self.file.getenv("SAVE_LOCATION")
        self.quotes_per_page = 10
        self.developers = self.file.getenv("DEVELOPERS")

    def is_owner(self, ctx):
        return ctx.message.author in self.developers

    @commands.command(name="qlist", aliases=["qfrom"])
    async def quotes_from_member(self, ctx, user: discord.Member):
        data = self.file.read_json(self.save_location)
        try:
            quotes = data[str(ctx.message.guild.id)][str(user.id)]["quotes"]
        except KeyError:
            await ctx.send(
                f"{user.display_name} currently does not have any quotes saved."
            )

        pages = MenuPages(
            source=QuoteMenu(ctx, quotes), clear_reactions_after=True, timeout=60.0
        )
        await pages.start(ctx)

    @commands.command(hidden=True, aliases=["allfrom"])
    @commands.is_owner()
    async def all_from_member(self, ctx, user: discord.Member):
        data = self.file.read_json(self.save_location)

        if type(user) is int:
            return

        quotes = []
        for server in data:
            if not str(user.id) in data[str(server)]:
                # print(f"No quotes from {user.display_name} in server: {server}")
                pass
            else:
                quotes += data[str(server)][str(user.id)]["quotes"]

        if not quotes:
            await ctx.send(f"There are no quotes from this user")
            return

        pages = MenuPages(
            source=QuoteMenu(ctx, quotes), clear_reactions_after=True, timeout=60.0
        )
        await pages.start(ctx)

    @commands.command(aliases=["randuser"])
    async def rand_from_user(self, ctx, user: discord.Member):
        data = self.file.read_json(self.save_location)
        quotes = data[str(ctx.message.guild.id)][str(user.id)]["quotes"]

        await ctx.send(quotes[random.randrange(0, len(quotes))]["msg"])

    async def send_quote(self, ctx, quote, message=None):
        if len(quote["image_attachments"]) <= 1:
            await ctx.send(message, embed=Emb().format(quote))
        else:  # deal with quotes with multiple attachments here
            print("multiple images")
            quote = AttachmentMenu(quote, message)
            await quote.start(ctx)

    @commands.command(aliases=["rand"])
    async def rand_from_server(self, ctx):
        # data = self.file.read_json(self.save_location)
        quote = []

        quotes = self.file.from_server(ctx.message.guild.id)

        if not quotes:
            await ctx.send("There are no quotes in this server. ")
        else:
            quote = random.choice(quotes)
            await self.send_quote(ctx, quote)


def setup(bot):
    bot.add_cog(read(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")
