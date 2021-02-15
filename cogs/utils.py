import discord
from discord.ext import commands
import os


class utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def dm(self, user: discord.Member, embed):
        if user.dm_channel == None:
            channel = await user.create_dm()
        else:
            channel = user.dm_channel

        await channel.send(embed=embed)

    async def member_count(self):
        servers = self.bot.guilds
        members = 0
        for server in servers:
            members += server.member_count

        return members


def setup(bot):
    bot.add_cog(utils(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")