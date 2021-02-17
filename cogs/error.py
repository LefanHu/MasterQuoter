import discord
from discord.ext import commands
import os
from lib.file_utils import File
import math
from datetime import datetime as dt
import traceback


class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def dm(self, user: discord.Member, embed):
        if user.dm_channel == None:
            channel = await user.create_dm()
        else:
            channel = user.dm_channel

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # if command has local error handler, return
        if hasattr(ctx.command, "on_error"):
            return

        # get the original exception
        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("This command has been disabled.")
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "This command is on cooldown, please retry in {}s.".format(
                    math.ceil(error.retry_after)
                )
            )
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please pass in all required arguments.")
            return

        await self.compose_report(ctx, error)
        # await ctx.send("error sent to developer")

    @commands.Cog.listener()
    async def on_error(self, err, *args, **kwargs):
        pass

    async def compose_report(self, ctx, error):
        time = ctx.message.created_at.strftime("%m/%d/%Y, %H:%M:%S")
        msg = ctx.message.content
        server = ctx.message.guild
        channel = ctx.message.channel
        member = ctx.message.author

        embed = discord.Embed(timestamp=dt.utcnow(), colour=0x00FFFF)

        embed.set_author(
            name="ERROR!",
            url="https://discordapp.com",
            icon_url=self.bot.user.avatar_url,
        )
        embed.set_footer(
            text=f"Error Report",
            icon_url=self.bot.user.avatar_url,
        )

        embed.add_field(name="**TIME**", value=time, inline=False)
        embed.add_field(name="**ERROR**", value=error, inline=False)
        embed.add_field(
            name="**TRACEBACK**",
            value="\n".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )[-1024:],
            inline=False,
        )
        embed.add_field(name="**MESSAGE**", value=f"Msg: {msg}", inline=False)
        embed.add_field(
            name="**CONTEXT DATA**",
            value=f"Server: {server.id} [{server.name}]\nChannel: {channel.id} [{channel.name}]\nMember: {member.id} [{member.display_name}]",
            inline=False,
        )

        # sends error to DEVELOPERS
        developers = File().getenv("DEVELOPERS").strip("][").split(", ")

        for developer in developers:
            user = await self.bot.fetch_user(int(developer))
            await self.dm(user, embed)


def setup(bot):
    bot.add_cog(Error(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")