from discord.ext.menus import ListPageSource
from discord import Embed
from datetime import datetime as dt


class QuoteMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx
        super().__init__(data, per_page=10)

    async def write_page(self, menu, fields=[]):
        offset = (menu.current_page * self.per_page) + 1
        len_data = len(self.entries)

        quote = self.entries[len_data - 1]
        name = quote["display_name"]
        avatar = quote["avatar_url"]

        embed = Embed(
            description=f"All of {name}'s quotes:",
            colour=self.ctx.author.colour,
            timestamp=dt.utcnow(),
        )

        embed.set_author(
            name=name,
            icon_url=avatar,
        )

        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} quotes.",
            icon_url=avatar,
        )

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        fields = []
        for entry in entries:
            if type(entry["msg"]) == list:
                entry["msg"] = "\n".join(entry["msg"])

            # trimming down the message to first 1000 characters
            entry["msg"] = entry["msg"][0:1000]

            if len(entry["image_attachments"]) != 0:
                entry["msg"] += f'\n+{len(entry["image_attachments"])} images'

            fields.append(
                (
                    f"<{entry['display_name']}> [{entry['message_id']}]",
                    f"```diff\n{entry['msg']}```",
                )
            )

        return await self.write_page(menu, fields)