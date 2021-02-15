from discord import Embed
from discord.ext import commands
from discord import __version__ as discord_version
from datetime import datetime, timedelta
from platform import python_version
from time import time
from psutil import Process, virtual_memory
import os


class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    @commands.command(alises=["about_bot", "bot_info"])
    async def about(self, ctx):
        embed = Embed(
            title="MasterQuoter Stats",
            colour=0x00FFFF,
            thumbnail=self.bot.user.avatar_url,
            timestamp=datetime.utcnow(),  # add this to error.py pls
        )

        proc = Process()
        with proc.oneshot():
            uptime = timedelta(seconds=time() - proc.create_time())
            cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
            mem_total = virtual_memory().total / (1024 ** 2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)

        fields = [
            ("Bot version", "0.0.1", False),
            ("Python version", python_version(), False),
            ("discord.py version", discord_version, False),
            ("Uptime", uptime, False),
            ("CPU time", cpu_time, False),
            (
                "Memory usage",
                f"{mem_usage:,.3f} / {mem_total:,.0f} MiB ({mem_of_total:.0f}%)",
                False,
            ),
            ("Users", f"{await self.bot.get_cog('utils').member_count():,}", False),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Example(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")
