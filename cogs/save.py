import discord
from discord.ext import commands, tasks
from lib.file_utils import File
from typing import Optional
from asyncio import TimeoutError

import pymongo

# use 135.0.54.232:27017 for accessing outside of network
client = pymongo.MongoClient(
    "mongodb://developer:masterbaiter@192.168.0.100:27017/masterquoter"
)

db = client.masterquoter


class Save(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.image_types = ["png", "jpeg", "gif", "jpg"]
        self.file = File()

    # getting a sample dataset
    @commands.command(aliases=["slh"])
    @commands.is_owner()
    async def save_last_hundred(self, ctx):
        """This command lets you save THE LAST HUNDRED quotes!\n"""

        messages = await ctx.channel.history(limit=100).flatten()
        for message in messages:
            await self.save_quote(ctx=ctx, user=message.author, msg=message.content)

    # Saving attachments associated with a message
    async def save_images(self, message):
        attachments = []
        for attachment in message.attachments:
            # print(attachment.filename)
            if self.file.is_image(attachment.filename):
                atch = {}
                atch["name"] = attachment.filename
                atch["id"] = attachment.id
                atch["url"] = attachment.url
                atch["proxy_url"] = attachment.proxy_url
                attachments.append(atch)
        return attachments

    async def save_attachments(self, message):
        attachments = []
        for attachment in message.attachments:
            # print(attachment.filename)
            if self.file.is_image(attachment.filename):
                pass
            else:
                atch = {}
                atch["name"] = attachment.filename
                atch["id"] = attachment.id
                atch["url"] = attachment.url
                atch["proxy_url"] = attachment.proxy_url
                attachments.append(atch)
        return attachments

    @commands.command(aliases=["qlast", "ql"])
    async def quote_last(
        self, ctx, user: discord.Member, section: Optional[int], lines: Optional[int]
    ):
        """
        Default: Saves the last 'continuous' message sent by user\n\n
        Section: The # of sections from that user to skip\n\n
        Lines: The # of lines to look for the specified section in, defaults to 100 with a limit of 200
        """
        if lines is None or lines > 200:
            lines = 100

        if not section:
            section = 0
        else:
            section *= -1
            section += 1
            # print(f"section = {section}")

        messages = await ctx.channel.history(limit=lines).flatten()

        msgs = []

        msg_indx = 0
        msg_len = len(messages)
        previous = False
        while msg_indx < msg_len:
            author_id = messages[msg_indx].author.id

            # if invoker is quoting self
            if msg_indx == 0 and author_id == user.id:
                pass
            elif section > 0:
                msg_indx -= 1
                author_id = messages[msg_indx].author.id
                while author_id == user.id:
                    try:  # currently saves 1 quote beyond the section
                        message = messages[msg_indx]
                        msgs.append(message)
                    except IndexError:
                        await ctx.send(
                            "That snippet is beyond the last {lines} messages"
                        )
                        break

                    msg_indx += 1
                    author_id = messages[msg_indx].author.id
                break
            # if previous user isn't
            elif author_id == user.id and previous != user.id:
                section += 1
                previous = user.id
            else:
                previous = False

            msg_indx += 1

        if not msgs:
            await ctx.send(
                f"Section {section*-1} of {user.name}'s messages in the last {lines} lines was not found"
            )

        await self.save_snippet(ctx, user, reversed(msgs))

    async def save_snippet(self, ctx, user: discord.Member, messages):
        msgs = []
        imgs = []
        files = []
        for message in messages:
            msgs.append(message.clean_content)
            imgs += await self.save_images(message)
            files += await self.save_attachments(message)

        if set(msgs) == {""} and not imgs:  # If all msgs are empty
            await ctx.send("Quote cannot be empty.")

        await self.save_quote(ctx, user, msg=msgs, imgs=imgs, files=files)

    # this is here so append_quote's extra parameters don't show up in help
    @commands.command(aliases=["qt"])
    async def quote(self, ctx, user: discord.Member, *, msg):
        """This handy dandy command allows you to save  things your friends have said!"""
        await self.save_quote(ctx, user, msg=msg)

    # Adds one quote to quote buffer

    async def save_quote(self, ctx, user: discord.Member, *, msg, imgs=[], files=[]):
        server_id = ctx.message.guild.id
        mem_id = user.id
        server = db.servers.find({"server_id": server_id})

        if not server:
            self.new_server(server_id)
            self.new_user(mem_id)
        elif not db.users.find_one({"user_id": mem_id}):
            self.new_user(mem_id)

        quote = {
            "msg": msg,
            "name": str(user),
            "display_name": user.display_name,
            "avatar_url": str(user.avatar_url),
            "time_stamp": int(ctx.message.created_at.timestamp()),
            "quote_id": server["quotes_saved"]
            if server != None
            else db.servers.find_one({"server_id": server_id})["quotes_saved"],
            "user_id": user.id,
            "server_id": ctx.message.guild.id,
            "channel_id": ctx.message.channel.id,
            "message_id": ctx.message.id,
            "image_attachments": await self.save_images(ctx.message)
            if imgs == None
            else imgs,
            "attachments": await self.save_attachments(ctx.message)
            if files == None
            else files,
        }

        # insert quotes into database
        db.servers.update_one({"server_id": server_id}, {"$push": {"quotes": quote}})
        db.users.update_one({"user_id": mem_id}, {"$push": {"quotes": quote}})
        # increment quote_saved
        db.servers.update_one({"server_id": server_id}, {"$push": {"quotes": quote}})

    @quote.error
    async def quote_error(self, ctx, exc):
        if isinstance(exc, commands.MissingRequiredArgument):
            if not ctx.message.attachments:
                await ctx.send("Quote cannot be empty.")
            else:
                imgs = await self.save_images(ctx.message)
                await self.save_quote(ctx, ctx.message.mentions[0], msg="", imgs=imgs)
        elif isinstance(exc, commands.MemberNotFound):
            await ctx.send("That member cannot be found.")
        else:
            print(exc)

    @commands.command(brief="Saves a quote by reactions")
    async def snip(self, ctx, lines: Optional[int]):
        user = ctx.author
        lines = 100 if lines == None else lines

        # ensures the reaction is intended for snipping use
        def is_user(payload):
            user_id = payload.user_id
            if user_id == user.id:
                return True
            return False

        try:
            reaction_one = await self.bot.wait_for(
                "raw_reaction_add", check=is_user, timeout=60.0
            )

            reaction_two = await self.bot.wait_for(
                "raw_reaction_add", check=is_user, timeout=60.0
            )

            msg_ids = [reaction_one.message_id, reaction_two.message_id]
            if set(msg_ids) == {reaction_one.message_id}:  # same message
                msg = await ctx.channel.fetch_message(reaction_one.message_id)
                await self.quote(ctx, msg.author, msg=msg.clean_content)
                return
            else:  # multiple messages
                messages = await ctx.channel.history(limit=lines).flatten()
                msgs = []
                for indx, message in enumerate(messages):
                    if message.id in msg_ids:
                        quoted_user = message.author
                        msgs.append(message)
                        indx += 1
                        while indx < len(messages):
                            if messages[indx].author != message.author:
                                await ctx.send(
                                    "Snippets(contains multiple authors) is not yet supported"
                                )
                                return
                            elif messages[indx].id in msg_ids:  # end has reached
                                msgs.append(messages[indx])
                                break
                            msgs.append(messages[indx])
                            indx += 1

                        # if snippet was cut off by the limit
                        if indx == len(messages):
                            await ctx.send(
                                "The full quote is not within {lines} messages."
                            )
                            return
                        break

                await self.save_snippet(ctx, quoted_user, msgs)
                await ctx.send("Snippet saved.")

        except TimeoutError:
            await ctx.send("Snip timed out")

    @commands.command(aliases=["rm", "remove"])
    async def remove_quote(self, ctx, quote_id):
        server_id = ctx.message.guild.id

        db.servers.update_one(
            {"server_id": server_id}, {"$pull": {"quotes": {"quote_id": quote_id}}}
        )

    def new_server(self, server_id):
        server = {
            "server_id": server_id,
            "quotes_saved": 0,
            "quoted_member_ids": [],
            "quotes": [],
        }
        db.servers.insert_one(server)

    def new_user(self, user_id):
        user = {"user_id": user_id, "quotes_saved": 0, "quotes": []}
        db.users.insert_one(user)


def setup(client):
    client.add_cog(Save(client))
    print(f"Cog '{File().file_name(__file__)}' has been loaded")
