import discord
from discord.ext import commands
from cogs.file_utils import File
import os
import json
import datetime


class read(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File(self.bot)
        self.save_location = self.file.get_env("SAVE_LOCATION")
        self.quotes_per_page = 10

    @commands.command(aliases=["qfrom"])
    async def quotes_from_member(self, ctx, user: discord.Member):
        data = self.file.read_json(self.save_location)
        quotes = data[str(ctx.message.guild.id)][str(user.id)]["quotes"]
        i = 0

        displayed_quotes = []
        while i < len(quotes):
            displayed_quotes.append(quotes[i])
            if len(displayed_quotes) == self.quotes_per_page:
                await ctx.send(embed=await self.compose_page(displayed_quotes))
                return
            i += 1
        await ctx.send(embed=await self.compose_page(displayed_quotes))

    async def compose_page(self, quote_list):
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


def setup(bot):
    bot.add_cog(read(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")