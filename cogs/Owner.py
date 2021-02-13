import discord
from discord.ext import commands
from cogs.file_utils import File
import os


class Owner(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.file = File(self.client)

    # owner must be the one who invoked the cog
    async def cog_check(self, ctx):
        if str(ctx.message.author.id) in self.file.get_env("DEVELOPERS"):
            return True
        await ctx.send(f"You are not the owner of this bot.")

    @commands.command(hidden=True)
    async def remove(self, ctx, file):
        self.file.file_remove(file)
        await ctx.send("File has been removed")

    @commands.command(hidden=True)
    async def list_files(self, ctx):
        files = ""
        for filename in os.listdir("."):
            files += filename + "\n"
        await ctx.send(files)


def setup(client):
    client.add_cog(Owner(client))
    print(f"Cog 'Owner' has been loaded")