from discord.ext import commands
from jikanpy import AioJikan
from jikanpy.exceptions import APIException
import os
from random import choice

from lib.utils import Utils

from discord.ext import menus


class Menu(menus.Menu):
    def __init__(self, results, formatter, timeout=10.0):
        super().__init__(timeout=timeout, clear_reactions_after=True)
        self.results = results
        self.result_indx = 0
        self.num_results = len(results)
        self.formatter = formatter

    async def send_initial_message(self, ctx, channel):
        embed = self.formatter(self.results[self.result_indx])
        return await channel.send(embed=embed)

    @menus.button("\N{LEFTWARDS BLACK ARROW}")
    async def on_left_arrow(self, payload):
        if self.result_indx == 0:
            pass
        else:
            self.num_results -= 1
            await self.message.edit(
                embed=self.formatter(self.results[self.result_indx])
            )

    @menus.button("\N{BLACK RIGHTWARDS ARROW}")
    async def on_right_arrow(self, payload):
        if self.result_indx == self.num_results - 1:
            pass
        else:
            self.result_indx += 1
            await self.message.edit(
                embed=self.formatter(self.results[self.result_indx])
            )

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, payload):
        self.stop()


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utils = Utils()

    # owner must be the one who invoked the cog
    async def cog_check(self, ctx):
        if ctx.message.author.id in self.bot.developers:
            return True
        await ctx.send(f"These commands are not ready yet.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online.")

    # implement jikan api here
    @commands.group(aliases=["jikan"], invoke_without_command=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def anime(self, ctx):
        """
        The developers of this bot likes anime. Therefore this is here too. This is rly rough rn but it'll get better (probably)

        **Command Group:**
            - `search`, `char|character`, more to come lol

        **Example:**
            - mq>anime search `name of anime`
            - mq>anime character `name of character`
            - mq>jikan char `MyAnimeList_ID`

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
    async def character(self, ctx, *, query):
        if query.isdigit():
            query = int(query)
            async with AioJikan() as jikan:
                results = await jikan.character(query)

            if not results:
                await ctx.send("No character results.")

            embed = self.utils.embed_jikan_character(results, id=True)
            await ctx.send(embed=embed)
        else:
            try:
                async with AioJikan() as jikan:
                    results = await jikan.search(search_type="character", query=query)
            except APIException:
                await ctx.send("API error (likely no results found)")
                return

            results = results["results"]
            result_menu = Menu(results, formatter=self.utils.embed_jikan_character)
            await result_menu.start(ctx)

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
