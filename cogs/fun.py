import discord
from discord.ext import commands
import os

from random import choice
from lib.file_utils import File
from lib.quote_embed import embed


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["lq"])
    async def loaded_questions(self, ctx):
        quote = choice(File().from_server(ctx.guild.id))
        quote = embed().format(quote)

        # quote = embed().format(quote)

        await ctx.send(f"Guess who said this quote!", embed=quote)


def setup(bot):
    bot.add_cog(events(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")