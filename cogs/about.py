from discord import Embed
from discord import __version__ as discord_version
from discord.ext import tasks, commands

from lib.file_utils import File
from datetime import datetime, timedelta
from platform import python_version
from psutil import Process, virtual_memory
from time import time
from lib.db import db


class About(commands.Cog):
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
        print(f" {guild.name} has joined us!")

        # sends message that new server was added
        channel = self.bot.get_channel(self.bot.log_channel)
        await channel.send(f"{guild.name} has joined us!")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.tracked_statuses["server_count"] -= 1
        print(f" {guild.name} has left us!")

        # sends message that server was removed
        channel = self.bot.get_channel(self.bot.log_channel)
        await channel.send(f"{guild.name} has removed us!")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.tracked_statuses["commands_processed"] += 1
        db.servers.find_one_and_update(
            {"_id": ctx.guild.id}, {"$inc": {"commands_invoked": 1}}
        )

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.name in ["quote", "snip", "quote_last"]:
            self.tracked_statuses["quotes_saved"] += 1

    def member_count(self):
        servers = self.bot.guilds
        members = 0
        for server in servers:
            members += server.member_count

        return members

    @commands.command(aliases=["about_bot"], brief="Shows info about this bot")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def about(self, ctx):
        """
        Just tells you what this bot is really about! :)

        **Example:**
            - mq>about

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/814618574777352192/unknown.png
        """

        prefix = db.servers.find_one({"_id": ctx.guild.id}, {"prefix": 1})["prefix"]

        description = f"""
        This bot is coded a group of 2 high school students who are bored out of their minds from quarantine. Hence, this bot.

        Anyway, here's some commands. For more information on how to use these commands... **ping MasterQuoter** or **use {prefix}help** `[command_name]`.

        {prefix}help `[command_name]` only works on the full length name of the command, shorter aliases will not work.

        **SAVING QUOTES/SNIPS**
            - `snip`, `quote`, `qlast`
        **REMOVING QUOTES/SNIPS**
            - `remove`, `rm_all`
        **DISPLAYING QUOTES/SNIPS**
            - `show_quote`, `show_snip`, `list_quotes`, `list_snips`, `random`
        **SETTINGS** (__manage_guild_perms__)
            - `prefix`, `blacklist`, `whitelist`, `pardon`, `restrict`, `delete_save_command`, `settings`
        **FUN**
            - `guess`, `anime`, `tictactoe`
        **OTHER COMMANDS**
            - `ping`, `help`, `about`, `invite`
        **THANKS**
            - @RadioactiveHydra#2570 (师傅 and Creator of MemeGenBot)
            - @Lunar#7231 (Minecraft God)
        **IDIOTS IN HIGH SCHOOL**
            - @Alex3000#4135
            - @Cuddles#2321

        """

        embed = Embed(
            title="📉About MasterQuoter📉",
            colour=0x00FFFF,
            thumbnail=self.bot.user.avatar_url,
            timestamp=datetime.utcnow(),
            description=f"{description}",
        )

        proc = Process()
        with proc.oneshot():
            uptime = timedelta(seconds=time() - proc.create_time())
            uptime = uptime - timedelta(microseconds=uptime.microseconds)
            cpu = proc.cpu_times()
            cpu_time = timedelta(seconds=(cpu).system + cpu.user)
            mem_total = virtual_memory().total / (1024 ** 2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)

        fields = [
            ("👌 Bot version 👌", self.bot.VERSION, True),
            ("🐍 Python version 🐍", python_version(), True),
            ("☄️ discord.py version 📸", discord_version, True),
            ("⏫ Uptime 🆙", uptime, True),
            ("💻 CPU time 🖥️", cpu_time, True),
            ("😢 Server Count 😢", f"{self.tracked_statuses['server_count']}", True),
            ("🥶 Users 🥶", f"{self.tracked_statuses['member_count']:,}", True),
            ("🗣️ Quotes Saved 🗣️", f"{self.tracked_statuses['quotes_saved']:,}", True),
            (
                "😔 Commands Run 😔",
                f"{self.tracked_statuses['commands_processed']:,}",
                True,
            ),
            (
                "🧠 Memory usage 🧠",
                f"{mem_usage:,.3f} / {mem_total:,.0f} MiB ({mem_of_total:.0f}%)",
                True,
            ),
            ("💌 Invite Link 💌", f"{self.bot.invite_link}", False),
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
        print("Stat tracking started")

    @update_stats.after_loop
    async def on_update_stats_cancel(self):
        await self.update_stats()
        print("Bot stats saved")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(File().file_name(__file__)[:-3])


def setup(bot):
    bot.add_cog(About(bot))
