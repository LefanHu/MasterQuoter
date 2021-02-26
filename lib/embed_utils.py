from random import choice
from discord import Embed, Colour
from datetime import datetime as dt


class embed:
    def format_quote(
        self,
        quote,
        *,
        show_image=True,
        image_num=None,
        hide_user=False,
        description=None,
    ):
        name = quote["display_name"] if not hide_user else "Unknown"
        avatar = quote["avatar_url"] if not hide_user else None
        msg = "\n".join(quote["msg"]) if type(quote["msg"]) == list else quote["msg"]
        image_num = 0 if image_num == None else image_num
        descriptor = ["wisdom", "quote", "statement"]

        embed = Embed(
            title=f"{name}:",
            description=msg if description == None else description,
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
                text=f"Channel: {quote['channel_name']}",
                icon_url=avatar,
            )

        if not quote["image_attachments"]:
            pass
        else:
            if show_image:
                # the below ensures image_num does not cause an index out of bounds error
                if image_num >= len(quote["image_attachments"]):
                    image_num = len(quote["image_attachments"]) - 1
                elif image_num < 0:
                    image_num = 0
                embed.set_image(url=quote["image_attachments"][image_num]["url"])

        return embed