from discord.ext import commands, tasks
from datetime import datetime as dt

import os
from dotenv import load_dotenv

from shutil import copyfile


class Backup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv()

        self.backup_quotes.start()

    @tasks.loop(minutes=5.0)
    async def backup_quotes(self):
        src = os.getenv("SAVE_LOCATION")
        file_name = str(dt.utcnow()) + "quotes.json"
        dst = os.getenv("BACKUP_LOCATION") + file_name
        # print(f"src = {src}\ndst = {dst}")

        copyfile(src, dst)


def setup(bot):
    bot.add_cog(Backup(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")