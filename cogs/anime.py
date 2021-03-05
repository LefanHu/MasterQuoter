import os
import tracemoepy
import aiohttp
from jikanpy import AioJikan
from typing import Optional
from random import choice
from discord.ext import menus, commands
from jikanpy.exceptions import APIException
from tracemoepy.errors import EmptyImage, EntityTooLarge, ServerError, TooManyRequests

from lib.utils import Utils
from lib.file_utils import File


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
            self.result_indx -= 1
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


class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.utils = Utils()
        self.file = File()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online.")

    # implement jikan api here
    @commands.group(
        aliases=["jikan"],
        invoke_without_command=True,
        brief="Some commands related to anime",
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def anime(self, ctx):
        """
        The developers of this bot likes anime. Therefore this is here too.

        **Command Group:**
            - `search`, `char|character`, `trace`

        **Examples:**
            - mq>anime search `name of anime`
            - mq>jikan search `MyAnimeList_ID`
            - mq>anime character `name of character`
            - mq>jikan char `MyAnimeList_ID`
            - mq>anime trace `(attach image to trace)`

        Example Usage:
        """
        await ctx.send("Let us recommend you an anime that we watch")

        anime_recommendations = ["42897", "39535", "37430", "28171", "32901"]
        await self.search(ctx=ctx, query=choice(anime_recommendations))

    @anime.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def search(self, ctx, *, query):
        if query.isdigit():
            query = int(query)
            async with AioJikan() as jikan:
                results = await jikan.anime(query)

            if not results:
                await ctx.send("No anime results.")

            embed = self.utils.embed_jikan_anime(results, id=True)
            await ctx.send(embed=embed)
        else:
            try:
                async with AioJikan() as jikan:
                    results = await jikan.search(search_type="anime", query=query)
            except APIException:
                await ctx.send("API error (likely no results found)")
                return

            results = results["results"]
            result_menu = Menu(results, formatter=self.utils.embed_jikan_anime)
            await result_menu.start(ctx)

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

    @anime.command(brief="Find out what anime your image is from")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def trace(self, ctx, image_url: Optional[str]):
        for attachment in ctx.message.attachments:
            if self.file.is_image(attachment.filename):
                image_url = attachment.url
                break

        if not image_url:
            await ctx.send("An image was not provided")
            return
        else:
            session = aiohttp.ClientSession()
            async with session as session:
                tracemoe = tracemoepy.AsyncTrace(session=session)
                try:
                    results = await tracemoe.search(image_url, is_url=True)
                except TooManyRequests:
                    await ctx.send(
                        "Trace-moe API limit reached, wait for a bit before trying again."
                    )
                    return
                except EntityTooLarge:
                    await ctx.send("Your image cannot be larger than 10mb")
                    return
                except EmptyImage:
                    await ctx.send("Your image was empty")
                    return
                except ServerError:
                    await ctx.send("An error occurred with trace-moe's servers.")
                    return

            embed = self.utils.embed_trace(results["docs"][0])
            embed.insert_field_at(
                1,
                name="Frames Searched",
                value=f"```{results['RawDocsCount']:,}```",
                inline=True,
            )
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Anime(bot))
