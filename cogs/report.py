import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from lib.file_utils import File
from datetime import datetime as dt


class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def dm(self, user: discord.Member, embed):
        if user.dm_channel == None:
            channel = await user.create_dm()
        else:
            channel = user.dm_channel

        await channel.send(embed=embed)

    @commands.command(brief="Reports an issue to developers")
    @commands.dm_only()
    @commands.cooldown(1, 1800, BucketType.user)  # 30 mins cooldown
    async def report(self, ctx):
        """
        This command is dm_only.
        Dm this bot with this command to report an issue with this bot to the developers!

        You can also send an image with any report in order to show the developers what's wrong!
        Usage Example:



        """

        msg = ctx.message.clean_content
        embed = discord.Embed(timestamp=dt.utcnow(), colour=0x00FFFF)
        embed.add_field(name="FROM:", value=f"From: {ctx.message.author}")
        embed.add_field(name="REPORT", value=f"Msg: {msg}", inline=False)

        for attachment in ctx.message.attachments:
            img = attachment.url
            embed.set_image(url=img)
        # Sends the error to direct messages

        for developer in self.bot.developers:
            user = await self.bot.fetch_user(int(developer))
            await self.dm(user, embed)

        await ctx.send("Thanks! Your report has been sent to the developers")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(File().file_name(__file__)[:-3])


def setup(bot):
    bot.add_cog(Report(bot))
