import discord
from discord.ext import commands
from lib.file_utils import File
from typing import Optional
from asyncio import TimeoutError
from lib.db import db, client


class Save(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.image_types = ["png", "jpeg", "gif", "jpg"]
        self.file = File()

    def cog_unload(self):
        client.close()
        print("db connection closed")

    async def cog_check(self, ctx):
        settings = db.servers.find_one({"_id": ctx.guild.id}, {"quoted_member_ids": 0})

        allowed = True
        if not settings["whitelist"] and not settings["blacklist"]:
            pass
        elif settings["whitelist"]:
            if ctx.message.author.id not in settings["allowed"]:
                allowed = False
        elif settings["blacklist"]:
            if ctx.message.author.id in settings["ignored"]:
                allowed = False

        if not allowed:
            await ctx.send("You are not allowed to manage quotes on this server.")

        return allowed

    # getting a sample dataset
    @commands.command(aliases=["slh"], brief="Saves last hundred")
    @commands.is_owner()
    async def save_last_hundred(self, ctx):
        """
        This command lets you save THE LAST HUNDRED quotes!\n

        For developper use only, sorry!

        """

        messages = await ctx.channel.history(limit=100).flatten()
        for message in messages:
            await self.save_quote(ctx=ctx, user=message.author, msg=message.content)

    # Saving attachments associated with a message
    async def save_images(self, message):
        attachments = []
        for attachment in message.attachments:
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

    @commands.command(
        aliases=["qlast", "ql"], brief="Quotes the last thing someone said"
    )
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

        user_exists = db.users.find_one({"_id": user.id})

        # create new user if not exists
        if not user_exists:
            # print("Adding user")
            self.new_user(user)

        quote = {
            "msg": msg,
            "name": user.name,
            "display_name": user.display_name,
            "avatar_url": str(user.avatar_url),
            "time_stamp": int(ctx.message.created_at.timestamp()),
            "user_id": user.id,
            "server_id": ctx.message.guild.id,
            "channel_id": ctx.message.channel.id,
            "message_id": ctx.message.id,
            "image_attachments": await self.save_images(ctx.message)
            if not imgs
            else imgs,
            "attachments": await self.save_attachments(ctx.message)
            if not files
            else files,
        }

        # insert quotes into database under db.users & increment quote count
        db.users.update_one(
            {"_id": mem_id},
            {"$push": {"quotes": quote}, "$inc": {"quotes_saved": 1}},
        )

        # add user's id to list if not in list & increment quote count
        db.servers.update_one(
            {"_id": server_id},
            {"$addToSet": {"quoted_member_ids": mem_id}, "$inc": {"quotes_saved": 1}},
        )

    @quote.error
    async def on_quote_error(self, ctx, exc):
        if isinstance(exc, commands.MissingRequiredArgument):
            if not ctx.message.attachments:
                await ctx.send("Quote cannot be empty.")
            else:
                imgs = await self.save_images(ctx.message)
                await self.save_quote(ctx, ctx.message.mentions[0], msg="", imgs=imgs)
        elif isinstance(exc, commands.MemberNotFound):
            await ctx.send("That member cannot be found.")
        elif isinstance(exc, commands.CheckFailure):
            pass
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

            # removes reactions to provide feedback snip was taken
            message_one = await ctx.channel.fetch_message(reaction_one.message_id)
            message_two = await ctx.channel.fetch_message(reaction_two.message_id)
            await message_one.remove_reaction(reaction_one.emoji, user)
            await message_two.remove_reaction(reaction_two.emoji, user)

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
                                    "Snippets (containing multiple authors) is not yet supported"
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

                await self.save_snippet(ctx, quoted_user, reversed(msgs))
                await ctx.send("Snippet saved.")

        except TimeoutError:
            await ctx.send("Snip timed out")

    def new_server(self, server):
        server = {
            "_id": server.id,
            "server_name": server.name,
            "prefix": "mq>",
            "quotes_saved": 0,
            "commands_invoked": 0,
            "del_on_save": False,
            "ignored": [],
            "allowed": [],
            "whitelist": False,
            "blacklist": False,
            "quoted_member_ids": [],
        }
        db.servers.insert_one(server)

    def new_user(self, user):
        user = {
            "_id": user.id,
            "user_name": user.name,
            "quotes_saved": 0,
            "quotes": [],
        }
        db.users.insert_one(user)

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.name in self.commands:
            settings = db.servers.find_one({"_id": ctx.guild.id}, {"del_on_save": 1})

            # delete save messages if completed
            if settings["del_on_save"] and not ctx.message.attachments:
                await ctx.message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(File().file_name(__file__)[:-3])

        # gets list of commands
        self.commands = [command.name for command in self.get_commands()]


def setup(client):
    client.add_cog(Save(client))
