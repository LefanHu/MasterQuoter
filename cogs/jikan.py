from discord.ext import commands
from jikanpy import AioJikan
import os
from random import choice

from lib.utils import Utils

import json


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utils = Utils()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online.")

    # implement jikan api here
    @commands.group(aliases=["jikan"], invoke_without_command=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def anime(self, ctx):
        """
        The developers of this bot likes anime. Therefore this is here too.

        **Command Group:**
            - `search`, `char|character`, more to come lol

        **Example:**
            - mq>anime search `name of anime`
            - mq>anime character `name of character`
            - mq>jikan char `name of character`

        **Note:**
            - Utilizes the jikan api

        Example Usage:
        """
        await ctx.send("Let us recommend you an anime that team 'MasterBaiters' watch")

        anime_recommendations = ["Mushoku Tensei", "Attack on titan"]
        await self.search(ctx=ctx, name=choice(anime_recommendations))

    @anime.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def search(self, ctx, *, name):
        async with AioJikan() as jikan:
            result = await jikan.search(search_type="anime", query=name)

        if not result:
            await ctx.send("No anime found")
            return

        embed = self.utils.embed_jikan_anime(result)
        await ctx.send(embed=embed)

    @anime.command(aliases=["char"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def character(self, ctx, *, name):
        async with AioJikan() as jikan:
            results = await jikan.search(search_type="character", query=name)

        if not results:
            await ctx.send("No character results.")

        embed = self.utils.embed_jikan_character(results)
        await ctx.send(embed=embed)

    @anime.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def season(self, ctx, *, year, season):
        pass

    @anime.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def top(self, ctx):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Basic(bot))
