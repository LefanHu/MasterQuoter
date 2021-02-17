from discord.ext import commands
from lib.file_utils import File
import os
from cogs.read import read


class Owner(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.file = File()
        self.read = read(client)

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

    @commands.command(hidden=True)
    async def list_servers(self, ctx):
        data = self.file.read_json()

        display_servers = ""
        for server in data:
            server = await self.client.fetch_guild(int(server))
            server_name = server.name
            display_servers += f"{server_name}\n"

        await ctx.send(display_servers)

    @commands.command(hidden=True)
    async def list_members(self, ctx):
        data = self.file.read_json()

        display_members = ""
        for server in data:
            for member in data[str(server)]:
                member_name = data[str(server)][str(member)]["quotes"][
                    len(data[str(server)][str(member)]["quotes"]) - 1
                ]["display_name"]
                display_members += f"{member_name}\n"

        await ctx.send(display_members)


def setup(client):
    client.add_cog(Owner(client))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")