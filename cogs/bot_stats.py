from discord.ext import commands, tasks
from os.path import basename
from cogs.file_utils import File
from cogs.utils import utils


class _bot_stats(commands.Cog):
    tracked_statuses = {
        "servers_count": 0,
        "servers_joined": 0,
        "member_count": 0,
        "quotes_saved": 0,
        "err_report_count": 0,
    }

    def __init__(self, bot):
        self.bot = bot
        self.file = File(self.bot)
        self.utils = utils(self.bot)

        self.stat_file = self.file.get_env("STATS")
        self.stats = self.file.read_json(self.stat_file)

        for stat in _bot_stats.tracked_statuses:
            try:
                stat_value = self.stats[stat]
            except KeyError as err:
                stat_value = None
            _bot_stats.tracked_statuses[stat] = stat_value

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        _bot_stats.tracked_statuses["server_count"] += 1
        _bot_stats.tracked_statuses["servers_joined"] += 1

    @commands.Cog.listener()
    async def on_server_removed(self):
        _bot_stats.tracked_statuses["server_count"] -= 1

    @tasks.loop(seconds=60.0)
    async def update_stats(self):
        _bot_stats.tracked_statuses["member_count"] = self.utils.member_count()
        self.file.write_json(self.stats, self.stat_file)


def setup(bot):
    bot.add_cog(_bot_stats(bot))
    print(f"Cog '{basename(__file__)}' has been loaded")
