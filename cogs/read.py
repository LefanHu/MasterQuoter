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

        quotes = []
        for server in data:
            if not str(user.id) in data[str(server)]:
                # print(f"No quotes from {user.display_name} in server: {server}")
                pass
            else:
                quotes += data[str(server)][str(user.id)]["quotes"]

        if not quotes:
            await ctx.send(f"There are no quotes from {user.mention}")
            return

        pages = MenuPages(
            source=QuoteMenu(ctx, quotes), clear_reactions_after=True, timeout=60.0
        )
        await pages.start(ctx)


    @commands.command(aliases =["qRand"])
    async def rand_quote(self, ctx, user: discord.Member):
        data = self.file.read_json(self.save_location);
        quotes = data[str(ctx.message.guild.id)][str(user.id)]["quotes"]



        await ctx.send(quotes[random.randrange(0, len(quotes))]['msg'])




    async def compose_page(self, quote_list):
        embed = discord.Embed(timestamp=datetime.datetime.utcfromtimestamp(1613242546))

        embed.set_author(
            name=f"{self.bot.user}",
            url="https://discordapp.com",
            icon_url=self.bot.user.avatar_url,
        )
        embed.set_footer(
            text="Brought to you by team 'MasterBaiters'",
            icon_url="https://cdn.discordapp.com/embed/avatars/0.png",
        )

        for quote in quote_list:
            # truncates message down to 75 characters
            message = (
                (quote["msg"][:75] + "..") if len(quote["msg"]) > 75 else quote["msg"]
            )
            embed.add_field(
                name=f"<{quote['display_name']}> [{quote['time']}]",
                value=f"Msg: {message}",
                inline=False,
            )

        return embed

    async def compose_list(self, list, page=1):

        embed = discord.Embed(timestamp=datetime.datetime.utcfromtimestamp(1613242546))

        embed.set_author(
            name=f"{self.bot.user}",
            url="https://discordapp.com",
            icon_url="https://cdn.discordapp.com/embed/avatars/0.png",
        )
        embed.set_footer(
            text="Brought to you by team 'MasterBaiters'",
            icon_url="https://cdn.discordapp.com/embed/avatars/0.png",
        )


def setup(bot):
    bot.add_cog(read(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")
