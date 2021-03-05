from discord.ext import commands
import os

from lib.confirm import Confirm


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # owner must be the one who invoked the cog
    async def cog_check(self, ctx):
        if ctx.message.author.id in self.bot.developers:
            return True
        await ctx.send(f"You are not the owner of this bot.")

    @commands.command(hidden=True)
    async def shutdown(self, ctx):
        confirmed = await Confirm("Are you sure you want to shutdown?").prompt(ctx)
        if confirmed:
            await ctx.send(f"Shutting down...")
            await self.bot.logout()

    @commands.command(hidden=True)
    async def clear(self, ctx, amount=1):
        await ctx.channel.purge(limit=amount)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Owner(bot))
