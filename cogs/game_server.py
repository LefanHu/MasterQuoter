from discord.ext import commands
import os, subprocess

from lib.confirm import Confirm


class Servers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.update_status.start()

    # checks if user invoking is in the game server
    async def cog_check(self, ctx):
        guild = self.bot.get_guild(849081194813587536)  # id of game server
        if ctx.message.author in guild.members:
            return True
        else:
            await ctx.send(f"You are not part of the player list.")

    @commands.command(aliases=["tsr"], hidden=True)
    @commands.cooldown(1, 20, commands.BucketType.guild)
    async def tmod_restart(self, ctx):
        """
        Restarts the modded terraria server through this bot (for personal use).

        **Example:**
            - mq>tmod_restart
            - mq>tsr

        **NOTE:**
            - Must be a member of specified game server to use this command
        """

        confirmed = await Confirm(
            "Are you sure you want to restart the tmod server?"
        ).prompt(ctx)
        if confirmed:
            await ctx.send(f"Restarting in 10 seconds")
            subprocess.call(
                f"scripts/tmod_restart.sh",
                shell=True,
            )
            await ctx.send(f"Restarting")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Servers(bot))
