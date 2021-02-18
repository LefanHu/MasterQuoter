import discord
from discord.ext import commands
import os
from asyncio import TimeoutError

from random import choice
from lib.file_utils import File
from lib.quote_embed import embed


class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["lq"])
    async def loaded_questions(self, ctx):
        attempts = 5

        quote = choice(File().from_server(ctx.guild.id))
        emb = embed().format(quote, hide_user=True)

        await ctx.send(
            f"Guess who said this quote! (5 guesses) Make at least 1 guess every 30 seconds.",
            embed=emb,
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


def setup(bot):
    bot.add_cog(events(bot))
    print(f"Cog '{os.path.basename(__file__)}' has been loaded")