from discord.ext import menus
import discord


class MyMenu(menus.Menu):
    def __init__(self, msg: discord.Embed):
        super().__init__(timeout=30.0, delete_message_after=True)
        self.msg = msg
        self.pages = len(msg)
        self.page = 0
        self.result = None

    async def send_initial_message(self, ctx, channel):
        return await channel.send(embed=self.msg[self.page])

    @menus.button("\N{LEFTWARDS BLACK ARROW}")
    async def on_thumbs_up(self, payload):
        if self.page > 0:
            self.page -= 1
        await self.message.edit(embed=self.msg[self.page])

    @menus.button("\N{BLACK RIGHTWARDS ARROW}")
    async def on_thumbs_down(self, payload):
        if self.page < self.pages - 1:
            self.page += 1
        await self.message.edit(embed=self.msg[self.page])

    @menus.button("\N{BLACK SQUARE FOR STOP}\ufe0f")
    async def on_stop(self, payload):
        self.stop()