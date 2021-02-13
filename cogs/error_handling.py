import discord
from discord.ext import commands
import os
from cogs.file_utils import File
from cogs.utils import utils
import math
import datetime
import traceback


class error_handle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # if command has local error handler, return
        if hasattr(ctx.command, "on_error"):
            return

        # get the original exception
        error = getattr(error, "original", error)

        # if isinstance(error, commands.CommandNotFound):
        #    raise commands.CommandNotFound

        if isinstance(error, commands.DisabledCommand):
            await ctx.send("This command has been disabled.")
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                "This command is on cooldown, please retry in {}s.".format(
                    math.ceil(error.retry_after)
                )
            )
            return

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please pass in all required arguments.")
            return

        await error_handle.compose_report(self, ctx, error)
        await ctx.send("error sent to developer")

    async def compose_report(self, ctx, error):
        time = ctx.message.created_at.strftime("%m/%d/%Y, %H:%M:%S")
        msg = ctx.message.content
        server = ctx.message.guild.id
        channel = ctx.message.channel.id
        member = ctx.message.author.id
        name = ctx.message.author.display_name

        embed = discord.Embed(timestamp=datetime.datetime.utcfromtimestamp(1613242546))

        embed.set_author(
            name="ERROR!",
            url="https://discordapp.com",
            icon_url="https://cdn.discordapp.com/embed/avatars/0.png",
        )
        embed.set_footer(
            text="footer text",
            icon_url="https://cdn.discordapp.com/embed/avatars/0.png",
        )

        embed.add_field(name="**TIME**", value=time, inline=False)
        embed.add_field(name="**ERROR**", value=error, inline=False)
        embed.add_field(
            name="**TRACEBACK**",
            value=traceback.format_exc(),
            inline=False,  # currently doesn't work :(
        )
        embed.add_field(name="**MESSAGE**", value=f"Msg: {msg}", inline=False)
        embed.add_field(
            name="**CONTEXT DATA**",
            value=f"Server: {server}\nChannel: {channel}\nMember: {member}",
            inline=False,
        )

        # sends error to DEVELOPERS
        developers = File(self.bot).get_env("DEVELOPERS").strip("][").split(", ")

        # getting dm function
        util = utils(self.bot)
        for developer in developers:
            user = await self.bot.fetch_user(int(developer))
            await util.dm(self, user, embed)


def setup(bot):
    bot.add_cog(error_handle(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")