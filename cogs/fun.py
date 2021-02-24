import discord
from discord.ext import commands
from asyncio import TimeoutError

import random
from lib.file_utils import File
from lib.quote_embed import embed

import pymongo

client = pymongo.MongoClient(File().getenv("DATABASE_URL"))
db = client.masterquoter

class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["lq"], brief="Fun little guessing game!")
    async def guess(self, ctx):
        """
        You ever wanna guess who said what stupid thing? This game is the perfect game for you!

        Default: Starts the guessing game
        Cmd: Does literally the same thing LOL
        """
        attempts = 5  # calculate this as a ratio later

        rand_user_id = random.choice(
            db.servers.find_one(
                {"_id": ctx.message.guild.id},
                {"_id": 0, "quoted_member_ids": 1},
            )["quoted_member_ids"]
        )
        quote = random.choice(
            db.users.find_one({"_id": rand_user_id}, {"_id": 0, "quotes": 1})[
                "quotes"
            ]
        )
        if not quote:  # ensures quote is not None
            await ctx.send("There are no quotes")
            return

        # sending the quote
        read = self.bot.get_cog("read")

        await read.send_quote(
            ctx,
            quote,
            message=f"Guess who said this quote! ({attempts} guesses) Make at least 1 guess every 30 seconds.",
            hide_user=True,
        )

        def is_correct(msg):
            return msg.author == ctx.message.author

        while attempts > 0:
            try:
                guess = await self.bot.wait_for(
                    "message", check=is_correct, timeout=30.0
                )

                if not guess.mentions:
                    pass
                elif len(guess.mentions) > 1:
                    attempts -= 1
                    await ctx.send(
                        f"You mentioned {len(guess.mentions)} users in your guess. You have {attempts} guesses left."
                    )
                else:
                    if guess.mentions[0].id == quote["user_id"]:
                        await ctx.send(
                            "You've guessed correctly!", embed=embed().format(quote)
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

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(File().file_name(__file__))


def setup(bot):
    bot.add_cog(events(bot))
