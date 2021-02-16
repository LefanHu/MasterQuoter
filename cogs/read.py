import discord
from discord.ext import commands

from cogs.file_utils import File
import os
import datetime
import random

from discord.ext.menus import MenuPages
from quote_menu import QuoteMenu


class read(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File(self.bot)
        self.save_location = self.file.get_env("SAVE_LOCATION")
        self.quotes_per_page = 10

    def is_owner(self, ctx):
        return ctx.message.author in self.file.get_env("DEVELOPERS")

    @commands.command(aliases=["qfrom"])
    async def quotes_from_member(self, ctx, user: discord.Member):
        data = self.file.read_json(self.save_location)
        quotes = data[str(ctx.message.guild.id)][str(user.id)]["quotes"]

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
    async def rand_quote(self, ctx, user: discord.Member):
        data = self.file.read_json(self.save_location)
        quotes = data[str(ctx.message.guild.id)][str(user.id)]["quotes"]

        await ctx.send(quotes[random.randrange(0, len(quotes))]["msg"])


def setup(bot):
    bot.add_cog(read(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")
