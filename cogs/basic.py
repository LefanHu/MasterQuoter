from discord.ext import commands
import os


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is online.")

    @commands.command(brief="Shows the latency of this bot")
    async def ping(self, ctx):
        "This shows the DWSP latency (Discord WebSocket protocol)"
        await ctx.send(f"Pong! Latency = {self.bot.latency * 1000}ms")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(events(bot))