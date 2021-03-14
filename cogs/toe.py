from discord import Member
from discord.ext import commands
from asyncio import TimeoutError
import os, math


class Toe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True, aliases=["toe"])
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def toetactic(self, ctx, user: Member):
        """
        A tic tac toe game made by @Cuddles. The alternative version is called "tic" and is made by @alex3000.

        __This command is hidden and will not appear in help :)__

        **Examples:**
            - mq>toe user (ping player you want to play against)

        **Note:**
            - stop (while game is active)

        Example Usage:
        """
        board = [["1️⃣", "2️⃣", "3️⃣"], ["4️⃣", "5️⃣", "6️⃣"], ["7️⃣", "8️⃣", "9️⃣"]]
        players = [ctx.message.author, user]
        if ctx.message.author.id == user.id:
            await ctx.send(
                "You're kinda lonely... maybe you should watch some heart warming anime..."
            )

        markers = ["🍑", "🍆"]

        def check_win(board):
            diag1 = True
            diag2 = True
            diag1_sym = board[0][0]
            diag2_sym = board[0][2]
            for row_num, row in enumerate(board):
                if len(set(row)) == 1:
                    return True
                if row[row_num] != diag1_sym:
                    diag1 = False
                if row[2 - row_num] != diag2_sym:
                    diag2 = False

                col = [row[row_num] for row in board]
                if len(set(col)) == 1:
                    return True

            # if any diagonals
            if any([diag1, diag2]):
                return True

        async def send_board(board_info, msg=None):
            game_board = ""
            for row in board_info:
                game_board += "".join(row) + "\n"

            if not msg:
                return await ctx.send(game_board)
            else:
                await msg.edit(content=game_board)

        def check(msg):
            if msg.author.id != player.id:
                return False
            elif msg.content == "stop":
                return True
            elif not msg.content.isdigit():
                return False
            elif int(msg.content) in taken_positions:
                return False
            elif int(msg.content) > 9 or int(msg.content) == 0:
                return False
            else:
                return True

        game_finished = False
        taken_positions = []
        msg = await send_board(board)
        while not game_finished:
            for indx, player in enumerate(players):
                await send_board(board, msg)
                player_name = player.display_name
                try:
                    move = await self.bot.wait_for("message", check=check, timeout=30.0)
                except TimeoutError:
                    await ctx.send("You took too long, the game is over.")
                    return
                if move.content == "stop":
                    await ctx.send("Game stopped")
                    return
                taken_positions.append(int(move.content))
                row = math.floor(int(move.content) / 3.1)
                col = math.ceil(int(move.content) % 3.1)
                board[row][col - 1] = markers[indx]

                if check_win(board):
                    game_finished = True
                    break
                elif sum(taken_positions) == 45:
                    game_finished = True
                    await ctx.send("It's a tie!")
                    return
                await move.delete()
        await ctx.send(f"{player_name} has won!")
        await send_board(board, msg)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Toe(bot))
