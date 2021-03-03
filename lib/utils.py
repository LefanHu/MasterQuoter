from random import choice
from discord import Embed, Colour
from datetime import datetime as dt

from lib.file_utils import File


class Utils:
    def __init__(self):
        self.file_utils = File()

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

    def format_snip(self, snip, page=0):
        descriptions = self.split_snip(snip)

        embed = Embed(
            title=f"Snippet: [`{snip['snip_id']}`]:",
            description=descriptions[page],
            colour=Colour.random(),
            timestamp=dt.fromtimestamp(snip["timestamp"]),
            thumbnail=snip["server_icon"],
        )
        embed.set_footer(
            icon_url=snip["server_icon"],
        )
        embed.add_field(
            name=f"**{snip['server_name']}**, in channel **{snip['channel_name']}**",
            value=f"```Snippet saved by: {snip['snipper']}```",
            inline=True,
        )
        if len(snip["images"]) > 0:
            embed.set_image(url=snip["images"][0])

        return embed

    def split_snip(self, snip, max_new_lines=10, max_chars=2000):
        sections = snip["sections"]
        descriptions = []
        description = ""
        for section in sections:
            messages = section["messages"]
            description += f"\n-<**{section['author_name']}**>-"
            for message in messages:
                if (
                    len(message + description) <= max_chars
                    and (description + message).count("\n") <= max_new_lines
                ):  # fits on page
                    description += f"\n{message}"
                else:  # doesn't fit on page, move to next page
                    descriptions.append(description)
                    description = f"-<**{section['author_name']} Continued...**>-"
                    description += f"\n{message}"

            if section["images"] > 0:
                description += f"\n<{section['images']} images>"

        descriptions.append(description)

        return descriptions

    def embed_trace(self, doc):
        embed = Embed(
            title=f"`{doc['filename'][:40]}...`",
            colour=Colour.random(),
            timestamp=dt.utcnow(),
        )
        titles = "\n".join(
            [doc["title_chinese"], doc["title_native"], doc["title_romaji"]]
        )
        fields = [
            (f"Similarity %", f"```{doc['similarity']:,.2f}%```", True),
            (f"Titles", f"```{titles}```", False),
            (f"Season", f"```{doc['season']} ```", True),
            (f"Episode", f"```{doc['episode']}```", True),
            (f"My Anime List ID", f"```{doc['mal_id']}```", True),
        ]
        embed.set_footer(
            text=f"From: {doc['from']/60:,.2f}mins To: {doc['to']/60:,.2f}mins"
        )

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        return embed

    def embed_jikan_anime(self, results, page=0):
        anime = results["results"][page]
        embed = Embed(
            title=f"**{anime['title']} [{anime['type']}]**",
            description=f"{anime['synopsis']}",
            colour=Colour.random(),
            timestamp=dt.utcnow(),
            url=anime["url"],
        )
        embed.set_thumbnail(url=anime["image_url"])

        startdate = "N/A" if not anime["start_date"] else anime["start_date"][:10]
        enddate = "N/A" if not anime["end_date"] else anime["end_date"][:10]

        fields = [
            ("Episodes", f"{anime['episodes']}", True),
            ("Score", f"{anime['score']}", True),
            ("My Anime List ID", f"{anime['mal_id']}", True),
            ("Start Date", startdate, True),
            ("End Date", enddate, True),
            ("Rated", f"{anime['rated']}", True),
            ("Airing", f"{anime['airing']}", True),
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=f"```{value}```", inline=inline)

        return embed

    def embed_jikan_character(self, result, id=False):
        if not result:
            return None

        if not id:
            animes = [anime["name"] for anime in result["anime"]]
            animes = "N/A" if not animes else ", ".join(animes)[:1000]

            mangas = [manga["name"] for manga in result["manga"]]
            mangas = "N/A" if not mangas else ", ".join(mangas)[:1000]

            alt_names = [alt_name for alt_name in result["alternative_names"]]
            alt_names = "N/A" if not alt_names else ", ".join(alt_names)[:2000]

            alt_names = ", ".join(result["alternative_names"])

            embed = Embed(
                title=f"**{result['name']}** My Anime List ID: [`{result['mal_id']}`]",
                description=f"Alternate Names: ```{alt_names} ```",
                colour=Colour.random(),
                timestamp=dt.utcnow(),
                url=result["url"],
            )
            embed.add_field(name="Animes", value=f"```{animes}```", inline=True)
            embed.add_field(name="Mangas", value=f"```{mangas}```", inline=True)
            embed.set_thumbnail(url=result["image_url"])

            return embed
        else:
            nicknames = ", ".join(result["nicknames"])
            animes = ", ".join([anime["name"] for anime in result["animeography"]])
            description = result["about"].replace("\\n", "")
            embed = Embed(
                title=f"**{result['name']} [My Anime List ID: {result['mal_id']}]**",
                description=f"```{description[:2000]}...```",
                colour=Colour.random(),
                timestamp=dt.utcnow(),
                url=result["url"],
            )
            embed.set_thumbnail(url=result["image_url"])
            embed.add_field(
                name="Nicknames", value=f"```{nicknames[:1000]}... ```", inline=False
            )
            embed.add_field(
                name="Animes", value=f"```{animes[:1000]}... ```", inline=False
            )

            return embed
