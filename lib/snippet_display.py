from discord.ext import menus
from discord import Embed

from datetime import datetime


class SnipInteractionMenu(menus.Menu):
    def __init__(self, ctx, snip, message=None):
        super().__init__(timeout=30.0, clear_reactions_after=True)
        self.ctx = ctx
        self.snip = snip
        self.instructions = "<◀️Images▶️> <⬅️Pages➡️>"
        self.chunk_length = 500
        self.lines_per_page = 8

        self.pages = self.split_pages(snip)

    def split_pages(self, snip):
        sections = snip["sections"]
        for section in enumerate(self.snip["sections"]):
            message = section["message"].splitlines()
            for line in message:
                # if the line is
                pass

            embed = Embed(
                description=f"All quotes from {self.ctx.guild.name if self.name is None else self.name}",
                colour=self.ctx.message.author.colour,
                timestamp=datetime.utcnow(),
            )
            pass

    async def send_initial_message(self, ctx, channel):
        if self.message != None:
            return await ctx.send(self.message, embed=self.embed)
        else:
            return await ctx.send(embed=self.embed)

    @menus.button("◀️")
    async def on_left_image(self, payload):
        if self.image_indx == 0:
            pass
        else:
            self.image_indx -= 1
            await self.message.edit(
                embed=self.embed.set_image(url=self.images[self.image_indx])
            )

    @menus.button("▶️")
    async def on_right_image(self, payload):
        if self.image_indx == self.image_num - 1:
            pass
        elif self.image_num == 0:
            pass
        else:
            self.image_indx += 1
            await self.message.edit(
                embed=self.embed.set_image(url=self.images[self.image_indx])
            )

    @menus.button("⬅️")
    async def on_left_chunk(self, payload):
        if self.chunk_indx == 0:
            pass
        else:
            self.chunk_indx -= 1

            self.embed = self.embed_util.format_quote(
                self.snip,
                image_num=self.image_indx,
                description=self.chunks[self.chunk_indx],
                hide_user=self.hide_user,
            )
            self.embed.set_footer(text=self.instructions)

            await self.message.edit(embed=self.embed)

    @menus.button("➡️")
    async def on_right_chunk(self, payload):
        if self.chunk_indx == self.chunk_num - 1:
            pass
        else:
            self.chunk_indx += 1

            self.embed = self.embed_util.format_quote(
                self.snip,
                image_num=self.image_indx,
                description=self.chunks[self.chunk_indx],
                hide_user=self.hide_user,
            )
            self.embed.set_footer(text=self.instructions)

            await self.message.edit(embed=self.embed)

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, payload):
        self.stop()