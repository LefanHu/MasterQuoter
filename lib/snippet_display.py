from discord.ext import menus
from lib.utils import Utils


class SnipInteractionMenu(menus.Menu):
    def __init__(self, snip, message=None):
        super().__init__(timeout=30.0, clear_reactions_after=True)
        self.snip = snip
        self.images = snip["images"]
        self.image_num = len(self.images)
        self.image_indx = 0

        self.instructions = "<◀️Images▶️> <⬅️Pages➡️>"

        self.utils = Utils()
        self.chunks = self.utils.split_snip(snip)
        self.chunk_indx = 0
        self.chunk_num = len(self.chunks)

        self.embed = self.utils.format_snip(self.snip)
        self.embed.set_footer(text=self.instructions)

    async def send_initial_message(self, ctx, channel):
        if self.message != None:
            return await ctx.send(self.message, embed=self.embed)
        else:
            return await ctx.send(embed=self.embed)

    @menus.button("◀️")
    async def previous_image(self, payload):
        if self.image_indx == 0:
            pass
        else:
            self.image_indx -= 1
            await self.message.edit(
                embed=self.embed.set_image(url=self.images[self.image_indx])
            )

    @menus.button("▶️")
    async def next_image(self, payload):
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
    async def previous_page(self, payload):
        if self.chunk_indx == 0:
            pass
        else:
            self.chunk_indx -= 1

            self.embed = self.utils.format_snip(self.snip, page=self.chunk_indx)
            self.embed.set_footer(text=self.instructions)
            await self.message.edit(embed=self.embed)

    @menus.button("➡️")
    async def next_page(self, payload):
        if self.chunk_indx == self.chunk_num - 1:
            pass
        else:
            self.chunk_indx += 1

            self.embed = self.utils.format_snip(self.snip, page=self.chunk_indx)
            self.embed.set_footer(text=self.instructions)
            await self.message.edit(embed=self.embed)

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, payload):
        self.stop()