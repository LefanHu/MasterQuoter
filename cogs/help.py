from typing import Optional
from discord.ext.commands.core import max_concurrency

from discord.ext.menus import ListPageSource, MenuPages
from lib.image_menu import ImageMenu

from discord import Embed
from discord.ext.commands import BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import Cog
from discord.utils import get

from os.path import basename


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
        help = command.help.split("Example Usage:")
        help_images = help[-1].split(",")

        embed = Embed(
            title=f"Help with `{command}`",
            description=syntax(command),
            colour=ctx.author.colour,
        )
        embed.set_image(url=help_images[0])

        embed.add_field(name="Command description", value=f"{help[0]}")

        if len(help_images) <= 1:  # if command contains only 1 help image
            embed.set_image(url=help[-1])
            await ctx.send(embed=embed)
        else:  # Multiple help images
            help_menu = ImageMenu(embed, help_images, timeout=45.0)
            await help_menu.start(ctx)

    @command(name="help", brief="Shows a menu with commands")
    @cooldown(3, 5, BucketType.user)
    async def show_help(self, ctx, cmd: Optional[str]):
        """
        Shows menu with all commands

        When provided with a `command_name`, usage of that command will be given

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/814629107072499712/unknown.png
        """
        if cmd is None:
            # hiding all hidden commands from help
            command_list = []
            for command in self.bot.commands:
                if command.hidden:
                    pass
                else:
                    command_list.append(command)

            menu = MenuPages(
                source=HelpMenu(ctx, command_list),
                clear_reactions_after=True,
                # delete_message_after=True,
                timeout=120.0,
            )
            await menu.start(ctx)
        else:
            command = get(self.bot.commands, name=cmd)
            if command:
                await self.cmd_help(ctx, command)
            else:
                await ctx.send("That command does not exist.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Help(bot))
