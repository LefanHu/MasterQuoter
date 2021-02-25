from discord.ext import commands
from time import time
import os


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online.")

    @commands.command(brief="Shows the latency of this bot")
    async def ping(self, ctx):
        "This shows the DWSP latency (Discord WebSocket protocol)"
        start = time()
        message = await ctx.send(f"Pong! Latency = {self.bot.latency * 1000:.2f}ms")
        end = time()

        await message.edit(
            content=f"Pong! Latency = {self.bot.latency*1000:,.0f} ms. Response time: {(end-start)*1000:,.0f} ms."
        )

    @commands.command(brief="returns an invite link to add this bot")
    async def invite(self, ctx):
        await ctx.send(self.bot.invite_link)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Basic(bot))