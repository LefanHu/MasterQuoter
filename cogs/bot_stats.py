from discord import Embed
from discord.ext import tasks, commands
from lib.file_utils import File

from discord import __version__ as discord_version
from datetime import datetime, timedelta
from platform import python_version
from time import time
from psutil import Process, virtual_memory


class _bot_stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File()
        self.stat_file = "data/stats.json"
        self.stats = self.file.read_json(self.stat_file)

        self.tracked_statuses = {
            "server_count": 0,
            "servers_joined": 0,
            "member_count": 0,
            "quotes_saved": 0,
            "commands_processed": 0,
        }

        for stat in self.tracked_statuses:
            try:
                stat_value = 0 if self.stats[stat] is None else self.stats[stat]
                # print(f'{stat} = {stat_value}')
            except KeyError:
                stat_value = 0
            self.tracked_statuses[stat] = stat_value

        self.update_stats.start()

    async def get_stat(self, stat):
        try:
            return self.tracked_statuses[stat]
        except KeyError:
            return 0

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.tracked_statuses["server_count"] += 1
        self.tracked_statuses["servers_joined"] += 1

    @commands.Cog.listener()
    async def on_server_removed(self, guild):
        self.tracked_statuses["server_count"] -= 1

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.tracked_statuses["commands_processed"] += 1

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.name == "quote":
            self.tracked_statuses["quotes_saved"] += 1
        elif ctx.command.name == "quote_last":
            self.tracked_statuses["quotes_saved"] += 1
        elif ctx.command.name == "snip":
            self.tracked_statuses["quotes_saved"] += 1

    def member_count(self):
        servers = self.bot.guilds
        members = 0
        for server in servers:
            members += server.member_count

        return members

    @commands.command(
        aliases=["about_bot", "bot_info"], brief="Shows info about this bot"
    )
    async def about(self, ctx):
        embed = Embed(
            title="📉MasterQuoter Stats📉",
            colour=0x00FFFF,
            thumbnail=self.bot.user.avatar_url,
            timestamp=datetime.utcnow(),
        )

        proc = Process()
        with proc.oneshot():
            uptime = timedelta(seconds=time() - proc.create_time())
            cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
            mem_total = virtual_memory().total / (1024 ** 2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)

        fields = [
            ("👌Bot version👌", "1.0.0", True),
            ("🐍Python version🐍", python_version(), True),
            ("☄️discord.py version📸", discord_version, True),
            ("⏫Uptime🆙", uptime, True),
            ("💻CPU time🖥️", cpu_time, True),
            (
                "🧠Memory usage🧠",
                f"{mem_usage:,.3f} / {mem_total:,.0f} MiB ({mem_of_total:.0f}%)",
                False,
            ),
            ("😭Users😭", f"{self.tracked_statuses['member_count']:,}", True),
            ("🍋Quotes Saved🍋", f"{self.tracked_statuses['quotes_saved']:,}", True),
            (
                "😔Commands Processed😔",
                f"{self.tracked_statuses['commands_processed']:,}",
                True,
            ),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=f"```{value}```", inline=inline)

        await ctx.send(embed=embed)

    @tasks.loop(minutes=5.0)
    async def update_stats(self):
        self.tracked_statuses["member_count"] = self.member_count()
        self.tracked_statuses["server_count"] = len(self.bot.guilds)
        self.file.write_json(self.tracked_statuses, self.stat_file)
        # print(f'commands_processed = {self.tracked_statuses["commands_processed"]}')

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()

    @update_stats.after_loop
    async def on_update_stats_cancel(self):
        await self.update_stats()
        print("Bot stats saved")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(File().file_name(__file__)[:-3])


def setup(bot):
    bot.add_cog(_bot_stats(bot))
