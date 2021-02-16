from discord.ext import commands, tasks
from os.path import basename
from cogs.file_utils import File
from cogs.utils import utils


class _bot_stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File(self.bot)
        self.utils = utils(self.bot)

        self.stat_file = self.file.get_env("STATS")
        self.stats = self.file.read_json(self.stat_file)

        self.tracked_statuses = {
            "server_count": 0,
            "servers_joined": 0,
            "member_count": 0,
            "quotes_saved": 0,
            "commands_processed": 0,
            "err_report_count": 0,
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

        if ctx.command.name == "compose_report":
            self.tracked_statuses["err_report_count"] += 1

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.name == "quote":
            self.tracked_statuses["quotes_saved"] += 1

    @tasks.loop(minutes=5.0)
    async def update_stats(self):
        self.tracked_statuses["member_count"] = await self.utils.member_count()
        self.tracked_statuses["server_count"] = len(self.bot.guilds)
        self.file.write_json(self.tracked_statuses, self.stat_file)

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(_bot_stats(bot))
    print(f"Cog '{basename(__file__)}' has been loaded")
