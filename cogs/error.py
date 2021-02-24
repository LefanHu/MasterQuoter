import discord
from discord.ext import commands
from discord.errors import Forbidden
from lib.file_utils import File
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
    async def on_command_error(self, ctx, exc):
        # if command has local exc handler, return
        if hasattr(ctx.command, "on_error"):
            return

        # get the original exception
        exc = getattr(exc, "original", exc)

        if isinstance(exc, commands.CommandNotFound):
            return
        elif isinstance(exc, commands.DisabledCommand):
            await ctx.send("This command has been disabled.")
            return
        elif isinstance(exc, commands.CommandOnCooldown):
            await ctx.send(
                f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs."
            )
        elif isinstance(exc, commands.MissingRequiredArgument):
            await ctx.send("Please pass in all required arguments.")
        elif isinstance(exc, commands.PrivateMessageOnly):
            await ctx.send(
                "This command can only be used when direct messaging the bot. "
            )
        elif isinstance(exc.original, Forbidden):
            await ctx.send("I do not have permission to do that.")
        else:
            await self.compose_report(ctx, exc)

    @commands.Cog.listener()
    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

        await self.stdout.send("An error occured.")

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

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(File().file_name(__file__)[:-3])


def setup(bot):
    bot.add_cog(Error(bot))
