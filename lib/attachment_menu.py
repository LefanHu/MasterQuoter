from discord.ext import menus
from lib.quote_embed import embed as emb


class AttachmentMenu(menus.Menu):
    def __init__(self, quote, msg=None):
        super().__init__(timeout=30.0, clear_reactions_after=True)
        self.quote = quote
        self.msg = msg
        self.embed = emb().format(quote)
        self.image_num = 0

    async def send_initial_message(self, ctx, channel):
        if not self.msg:
            return await channel.send(embed=self.embed)
        else:
            return await channel.send(f"{self.msg}", embed=self.embed)

    @menus.button("\N{LEFTWARDS BLACK ARROW}")
    async def on_left_arrow(self, payload):
        self.image_num -= 1
        await self.message.edit(
            embed=emb().format(self.quote, image_num=self.image_num)
        )

    @menus.button("\N{BLACK RIGHTWARDS ARROW}")
    async def on_right_arrow(self, payload):
        self.image_num += 1
        await self.message.edit(
            embed=emb().format(self.quote, image_num=self.image_num)
        )

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, payload):
        self.stop()