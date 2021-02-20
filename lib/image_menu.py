from discord.ext import menus
from lib.quote_embed import embed as emb


class ImageMenu(menus.Menu):
    def __init__(self, quote, msg=None):
        super().__init__(timeout=30.0, clear_reactions_after=True)
        self.quote = quote
        self.msg = msg
        self.embed = emb().format(quote)
        self.images = self.quote["image_attachments"]
        self.image_count = len(self.images)
        self.image_num = 0

    async def send_initial_message(self, ctx, channel):
        if not self.msg:
            return await channel.send(embed=self.embed)
        else:
            return await channel.send(f"{self.msg}", embed=self.embed)

    @menus.button("\N{LEFTWARDS BLACK ARROW}")
    async def on_left_arrow(self, payload):
        if self.image_num == 0:
            pass
        else:
            self.image_num -= 1
            await self.message.edit(
                embed=self.embed.set_image(url=self.images[self.image_num]["url"])
            )

    @menus.button("\N{BLACK RIGHTWARDS ARROW}")
    async def on_right_arrow(self, payload):
        if self.image_num == self.image_count - 1:
            pass
        else:
            self.image_num += 1
            await self.message.edit(
                embed=self.embed.set_image(url=self.images[self.image_num]["url"])
            )

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, payload):
        self.stop()