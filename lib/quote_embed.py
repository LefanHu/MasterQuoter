from discord import Embed, Colour
from datetime import datetime as dt


class embed:
    def format(self, quote, *, attachment=None):
        name = quote["display_name"]
        avatar = quote["avatar_url"]
        msg = quote["msg"].join("\n") if type(quote["msg"]) == list else quote["msg"]
        attachment = 0 if attachment == None else attachment

        embed = Embed(
            title=f"{name}:",
            description=msg,
            colour=Colour.random(),
            timestamp=dt.fromtimestamp(quote["time_stamp"]),
        )

        embed.set_author(
            name=name,
            icon_url=avatar,
        )

        embed.set_footer(
            text=f"{name}'s wisdom",
            icon_url=avatar,
        )

        if not quote["attachments"]:
            pass
        else:
            # this will change if the original attachment message has been deleted
            embed.set_image(url=quote["attachments"][attachment]["url"])

        # dealing with attachments

        return embed