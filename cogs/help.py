from typing import Optional

from discord.ext.menus import ListPageSource, MenuPages

from discord import Embed
from discord.ext.commands import command
from discord.ext.commands import Cog
from discord.utils import get


from discord import __version__ as discord_version
from datetime import datetime, timedelta
from platform import python_version
from time import time
from psutil import Process, virtual_memory
import os


def syntax(command):
    cmd_and_aliases = "|".join([str(command), *command.aliases])
    params = []

    for key, value in command.params.items():
        if key not in ("self", "ctx"):
            params.append(f"[{key}]" if "NoneType" in str(value) else f"<{key}>")

    params = " ".join(params)

    return f"```{cmd_and_aliases} {params}```"


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        super().__init__(data, per_page=5)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(
            title="Help",
            description="Welcome to MasterQuoter's help dialog!",
            colour=self.ctx.author.colour,
        )
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} commands."
        )

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        for entry in entries:
            fields.append((entry.brief or "No description", syntax(entry)))

        return await self.write_page(menu, fields)


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    async def cmd_help(self, ctx, command):
        """shows this message"""
        embed = Embed(
            title=f"Help with `{command}`",
            description=syntax(command),
            colour=ctx.author.colour,
        )
        embed.add_field(name="Command description", value=command.help)
        await ctx.send(embed=embed)

    @command(name="help", brief="shows this message")
    async def show_help(self, ctx, cmd: Optional[str]):
        """description of help command"""
        if cmd is None:
            menu = MenuPages(
                source=HelpMenu(ctx, list(self.bot.commands)),
                clear_reactions_after=True,
                # delete_message_after=True,
                timeout=120.0,
            )
            await menu.start(ctx)
        else:
            if (command := get(self.bot.commands, name=cmd)) :
                await self.cmd_help(ctx, command)
            else:
                await ctx.send("That command does not exist.")

    @command(aliases=["about_bot", "bot_info"], brief="Shows info about this bot")
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
            embed.add_field(name=name, value=f"```{value}```", inline=inline)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")
