from discord.ext import commands
import os, subprocess

from lib.confirm import Confirm


class Servers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.update_status.start()

    # checks if user invoking is in the game server
    async def cog_check(self, ctx):
        guild = self.bot.get_guild(795405783155343361)  # id of game server
        if ctx.message.author in guild.members:
            return True
        else:
            await ctx.send(f"You are not part of the player list.")

    @commands.command(hidden=True)
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def tmod_restart(self, ctx):
        """
        This shows the DWSP latency (Discord WebSocket protocol) as well as the response latency of the bot.

        **Example:**
            - mq>ping

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/814868595611664424/unknown.png
        """

        confirmed = await Confirm(
            "Are you sure you want to restart the tmod server?"
        ).prompt(ctx)
        if confirmed:
            subprocess.call(
                f"scripts/tmod_restart.sh",
                shell=True,
            )
            await ctx.send(f"Restarting in 10 seconds")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Servers(bot))
