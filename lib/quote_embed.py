from random import choice
from discord import Embed, Colour
from datetime import datetime as dt


class embed:
    def format(self, quote, *, image_num=None, hide_user=False):
        name = quote["display_name"] if not hide_user else "Unknown"
        avatar = quote["avatar_url"] if not hide_user else None
        msg = quote["msg"].join("\n") if type(quote["msg"]) == list else quote["msg"]
        image_num = 0 if image_num == None else image_num
        descriptor = ["wisdom", "quote", "statement"]

        embed = Embed(
            title=f"{name}:",
            description=msg,
            colour=Colour.random(),
            timestamp=dt.fromtimestamp(quote["time_stamp"]),
        )

        if hide_user:
            embed.set_author(name=name)
            embed.set_footer(text=f"{name}'s {choice(descriptor)}")
        else:
            embed.set_author(
                name=name,
                icon_url=avatar,
            )

            embed.set_footer(
                text=f"{name}'s wisdom",
                icon_url=avatar,
            )

        if not quote["image_attachments"]:
            pass
        else:
            embed.set_image(url=quote["image_attachments"][image_num]["url"])

        # dealing with attachments

        return embed