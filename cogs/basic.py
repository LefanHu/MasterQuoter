from discord.ext import commands
from time import time
import os


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Shows the latency of this bot")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def ping(self, ctx):
        """
        This shows the DWSP latency (Discord WebSocket protocol) as well as the response latency of the bot.

        **Example:**
            - mq>ping

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/814868595611664424/unknown.png
        """
        start = time()
        message = await ctx.send(f"Pong! Latency = {self.bot.latency * 1000:.2f}ms")
        end = time()

        await message.edit(
            content=f"Pong! Latency = {self.bot.latency*1000:,.0f} ms. Response time: {(end-start)*1000:,.0f} ms."
        )

    @commands.command(brief="Sends an invite link to add this bot to another server! ")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def invite(self, ctx):
        """
        This sends an invite link for the bot to join your server.

        **Example:**
            - mq>invite

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/815985551345582130/unknown.png
        """
        await ctx.send(self.bot.invite_link)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Basic(bot))
