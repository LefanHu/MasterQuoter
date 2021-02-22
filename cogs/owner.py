from discord.ext import commands
from lib.file_utils import File
import os

import pymongo


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File()
        self.developers = self.file.getenv("DEVELOPERS")

    # owner must be the one who invoked the cog
    async def cog_check(self, ctx):
        if str(ctx.message.author.id) in self.developers:
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

    @commands.command(hidden=True)
    async def clear_db(self, ctx, confirm):
        if confirm != "CONFIRM":
            await ctx.send("`CONFIRM` is required.")
            return

        client = pymongo.MongoClient(
            "mongodb://developer:masterbaiter@192.168.0.100:27017/masterquoter"
        )
        db = client.masterquoter

        # clears all servers
        db.servers.delete_many({})
        db.users.delete_many({})

        await ctx.send("db cleared.")


def setup(bot):
    bot.add_cog(Owner(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")
