from discord.ext import commands
from asyncio import TimeoutError
from typing import Optional
from lib.embed_utils import embed
from lib.db import db
from os.path import basename
import random


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = []

    def session_exists(self, channel_id: int):
        if channel_id in self.sessions:
            return True
        return False

    def remove_session(self, channel_id: int):
        self.sessions.remove(channel_id)

    @commands.command(aliases=["gs"], brief="Fun little guessing game!")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def guess(self, ctx, guesses: Optional[int]):
        """
        You ever wanna guess who said what stupid thing? This starts a game
        where a random quote is displayed (hiding the author of the quote) and
        the first person to ping the author of the quote is granted the guess.

        **Example:**
            - mq>guess
            - mq>gs 10
            - stop (while game is active to stop game)

        **Notes:**
            - Max guesses is 10, any more than 10 will default to 5 attempts.

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/814945245313761300/unknown.png
        """

        if self.session_exists(ctx.message.channel.id):
            return  # no more than one game session per channel
        else:
            self.sessions.append(ctx.message.channel.id)

        attempts = (
            5 if not guesses or guesses > 10 else guesses
        )  # calculate this as a ratio later

        # getting quoted members from server in database
        member_ids = db.servers.find_one(
            {"_id": ctx.guild.id}, {"_id": 0, "quoted_member_ids": 1}
        )["quoted_member_ids"]

        # getting quotes from listed users in database
        cursor = db.users.find(
            {"_id": {"$in": member_ids}},
            {
                "_id": 0,
                "quotes": 1,
            },
        )

        quotes = []
        quote_sections = list(cursor)
        for quote_section in quote_sections:
            for quote in quote_section["quotes"]:
                if quote["server_id"] == ctx.message.guild.id:
                    quotes.append(quote)

        if not quotes:  # ensures quote is not None
            await ctx.send("There are no quotes")
            self.remove_session(ctx.message.channel.id)
            return
        else:
            quote = random.choice(quotes)

        # sending the quote
        read = self.bot.get_cog("Read")
        await read.send_quote(
            ctx,
            quote,
            message=f"Guess who said this quote! ({attempts} guesses) Make at least 1 guess every 30 seconds.",
            hide_user=True,
        )

        prefix = db.servers.find_one({"_id": ctx.message.guild.id}, {"prefix": 1})[
            "prefix"
        ]

        def is_correct(msg):
            is_author = msg.author == ctx.message.author
            starts_with_prefix = msg.content.startswith(prefix)
            if is_author and not starts_with_prefix:
                return True
            return False

        while attempts > 0:
            try:
                guess = await self.bot.wait_for(
                    "message", check=is_correct, timeout=30.0
                )

                if not guess.mentions or guess.clean_content == "stop":
                    pass
                elif len(guess.mentions) > 1:
                    attempts -= 1
                    await ctx.send(
                        f"You mentioned {len(guess.mentions)} users in your guess. You have {attempts} guesses left."
                    )
                else:
                    if guess.mentions[0].id == quote["user_id"]:
                        await ctx.send(
                            "You've guessed correctly!",
                            embed=embed().format_quote(quote),
                        )
                        break
                    else:
                        attempts -= 1
                        await ctx.send(f"Incorrect. {attempts} guesses left")
            except TimeoutError:
                attempts -= 1
                await ctx.send(
                    f"You took too long to guess. You now have {attempts} guesses."
                )
        self.remove_session(ctx.message.channel.id)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(events(bot))
