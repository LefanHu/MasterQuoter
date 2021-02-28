from discord.ext.menus import ListPageSource
from discord import Embed
from datetime import datetime as dt


class SnippetMenu(ListPageSource):
    def __init__(self, ctx, data, name=None, icon_url=None):
        self.ctx = ctx
        self.name = name
        self.icon_url = icon_url
        super().__init__(data, per_page=3)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        embed = Embed(
            description=f"```Snippets from {self.ctx.guild.name if self.name is None else self.name}```",
            colour=self.ctx.author.colour,
            timestamp=dt.utcnow(),
        )

        embed.set_author(
            name=self.name,
            icon_url=self.icon_url,
        )

        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} snippets.",
            icon_url=self.icon_url,
        )

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        for snip in entries:
            description = ""

            # trimming down the message to first 1000 characters
            for section in snip["sections"]:
                description += f"\n-{section['author_name']}-{section['message']}"

                if section["images"] != 0:
                    description += f"\n+{section['images']} images"

            description = description[0:200]
            description.strip("`")

            fields.append(
                (
                    f"`Snip ID: {snip['snip_id']}`",
                    f"```diff\n{description}```",
                )
            )

        return await self.write_page(menu, fields)