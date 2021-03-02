from discord.ext import commands
from typing import Optional
import tracemoepy
import os
import aiohttp
from tracemoepy.errors import EmptyImage, EntityTooLarge, ServerError, TooManyRequests

from lib.file_utils import File
from lib.utils import Utils

import json


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File()
        self.utils = Utils()

    @commands.command(brief="Find out what anime your image is from")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def trace(self, ctx, image_url: Optional[str]):
        """
        Returns whatever result trace.moe thinks your image is from.

        Don't judge why this command exists in a bot for saving quotes. We like anime so therefore this is here. Btw, we recommend `Mushoku Tensei` (**Disclaimer:** Not suitable for younger audiences).

        **Example:**
            - mq>trace `image_url`
            - mq>trace (attach the image to this command instead of using the url)

        **Note:**
            - Cooldown Type: Channel (Length: 60 seconds)
            - If an image is attached, that image will be prioritized over the url if both are provided
            - Newly released anime probably won't be found :/

        Example Usage:
        """

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

            # for debugging
            # with open("trace.json", "w") as f:
            #     json.dump(results, f, indent=4)

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
    bot.add_cog(Basic(bot))
