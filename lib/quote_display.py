from discord.ext import menus
from lib.utils import Utils


class QuoteInteractionMenu(menus.Menu):
    def __init__(self, quote, message=None, hide_user=False):
        super().__init__(timeout=30.0, clear_reactions_after=True)
        self.quote = quote
        self.message = message
        self.hide_user = hide_user
        self.instructions = "◀️ ▶️ <Navigate Images> ⬅️ ➡️ <Next Page>"
        chunk_length = 1000  # num of characters per chunk

        messages = (
            "\n".join(self.quote["msg"])
            if type(self.quote["msg"]) == list
            else self.quote["msg"]
        )

        self.chunks = [
            messages[i : i + chunk_length]
            for i in range(0, len(messages), chunk_length)
        ]
        self.chunk_num = len(self.chunks)
        self.chunk_indx = 0

        self.images = quote["image_attachments"]
        self.image_num = len(self.images)
        self.image_indx = 0

        self.utils = Utils()

        # Initial message
        self.embed = self.utils.format_quote(
            self.quote,
            image_num=self.image_indx,
            description=self.chunks[self.chunk_indx],
            hide_user=self.hide_user,
        )
        self.embed.set_footer(text=self.instructions)

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
                embed=self.embed.set_image(url=self.images[self.image_indx]["url"])
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
                embed=self.embed.set_image(url=self.images[self.image_indx]["url"])
            )

    @menus.button("⬅️")
    async def on_left_chunk(self, payload):
        if self.chunk_indx == 0:
            pass
        else:
            self.chunk_indx -= 1

            self.embed = self.utils.format_quote(
                self.quote,
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

            self.embed = self.utils.format_quote(
                self.quote,
                image_num=self.image_indx,
                description=self.chunks[self.chunk_indx],
                hide_user=self.hide_user,
            )
            self.embed.set_footer(text=self.instructions)

            await self.message.edit(embed=self.embed)

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, payload):
        self.stop()