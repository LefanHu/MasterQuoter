from discord import Game
from discord.ext import commands
import traceback
import os

from lib.confirm import Confirm


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # owner must be the one who invoked the cog
    async def cog_check(self, ctx):
        if ctx.message.author.id in self.bot.developers:
            return True
        await ctx.send(f"You are not the owner of this bot.")

    @commands.command(hidden=True)
    async def shutdown(self, ctx):
        """
        Shuts down the bot (Owner only).

        **Examples:**
            - mq>shutdown

        Example Usage:
        """
        confirmed = await Confirm("Are you sure you want to shutdown?").prompt(ctx)
        if confirmed:
            await ctx.send(f"Shutting down...")
            await self.bot.logout()

    @commands.command(hidden=True)
    async def clear(self, ctx, amount=1):
        """
        Purges the specified amount of messages from the channel (Owner only).

        **Examples:**
            - mq>clear
            - mq>clear 10

        Example Usage:
        """
        await ctx.channel.purge(limit=amount)

    @commands.command(hidden=True)
    async def send_to(self, ctx, channel_id: int, *, msg):
        """
        Sends a message to the specified channel (Owner only).

        **Examples:**
            - mq>send_to `channel_id` some random message here

        Example Usage:
        """
        channel = self.bot.get_channel(channel_id)
        if not channel:
            await ctx.send("Could not get that channel.")
            return
        await channel.send(msg)

    @commands.command(name="aset", hidden=True)
    async def activity_set(self, ctx, *, status):
        """
        Sets a custom activity for the bot (Owner only).

        **Examples:**
            - mq>aset `Activity message`

        Example Usage:
        """
        await self.bot.change_presence(activity=Game(name=status))

    @commands.command(hidden=True)
    async def servers(self, ctx):
        """
        Displays the servers this bot is in (Owner only).

        **Examples:**
            - mq>servers

        Example Usage:
        """
        await ctx.send(", ".join([guild.name for guild in self.bot.guilds][:2000]))

    @commands.command(hidden=True)
    async def reload(self, ctx, module: str):
        """
        Reloads a cog (Owner only).

        **Examples:**
            - mq>reload `name_of_cog`

        **List of Cogs:**
            - `about`, `anime`, `basic`, `error`, `fun`, `help`, `owner`, `public`, `read`, `remove`, `save`, `settings`, `toe`

        Example Usage:
        """
        try:
            self.bot.unload_extension(f"cogs.{module}")
            self.bot.load_extension(f"cogs.{module}")
        except Exception as e:
            trace = "\n".join(traceback.format_exception(type(e), e, e.__traceback__))[
                :-2000
            ]
            await ctx.send(f"\N{PISTOL}\n{e}: {trace}")
        else:
            await ctx.send("\N{OK HAND SIGN}")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Owner(bot))
