from discord.ext import commands, tasks
from os.path import basename
from lib.file_utils import File


class _bot_stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = File()
        self.stat_file = self.file.getenv("STATS")
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

    async def member_count(self):
        servers = self.bot.guilds
        members = 0
        for server in servers:
            members += server.member_count

        return members

    @tasks.loop(seconds=5.0)
    async def update_stats(self):
        self.tracked_statuses["member_count"] = await self.member_count()
        self.tracked_statuses["server_count"] = len(self.bot.guilds)
        self.file.write_json(self.tracked_statuses, self.stat_file)
        # print(f'commands_processed = {self.tracked_statuses["commands_processed"]}')

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(_bot_stats(bot))
    print(f"Cog '{basename(__file__)}' has been loaded")
