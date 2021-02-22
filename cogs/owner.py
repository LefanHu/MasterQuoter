from discord.ext import commands
import os

from bot import DEVELOPERS


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # owner must be the one who invoked the cog
    async def cog_check(self, ctx):
        if str(ctx.message.author.id) in DEVELOPERS:
            return True
        await ctx.send(f"You are not the owner of this bot.")

    @commands.command(hidden=True)
    async def clear(self, ctx, amount=1):
        await ctx.channel.purge(limit=amount)

    @commands.command(hidden=True)
    async def shutdown(self, ctx):
        await ctx.send("Shutting down")
        await self.bot.logout()

        print("Bot has been shut down.")


def setup(bot):
    bot.add_cog(Owner(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")
