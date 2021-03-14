import discord
from discord.ext import commands
from lib.file_utils import File
from typing import Optional
from asyncio import TimeoutError
from lib.db import db, client


class Save(commands.Cog):
    def __init__(self, client):
        self.bot = client
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

    @commands.command(aliases=["ql"], brief="Quotes the last thing someone said")
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def qlast(
        self, ctx, user: discord.Member, section: Optional[int], lines: Optional[int]
    ):
        """
        Saves the last section of *continuous messages* from that user.

        **section:** This specifies the # of sections to pass before saving.

        **lines:** This specifies how many lines in the channel to look (max 200)

        **Examples:**
            - mq>qlast @alex3000
            - mq>qlast @alex3000 2
            - mq>qlast @alex3000 2 150

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/815989465474007081/unknown.png,
        https://cdn.discordapp.com/attachments/795405783155343365/815989508137811988/unknown.png
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
    @commands.command(aliases=["qt", "q"], brief="Saving quotes of other people")
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def quote(self, ctx, user: discord.Member, *, msg):
        """
        This handy dandy command allows you to save things your friends have said!

        **Examples:**
            - mq>quote @alex3000 `MAKE UP A_RANDOM_MESSAGE IF YOU WANT` `>:)`
            - mq>qt @alex3000 `message here`
            - mq>q @alex3000 `message here`

        **Note:**
            - When the save command contains a image attachment, the command will **NOT** be deleted if delete `save commands on completion` is `enabled`.
            - This is because the image url becomes __invalid__ as soon as it is deleted.

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/815987934360371300/unknown.png
        """
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
            "public": False,
            "name": user.name,
            "display_name": user.display_name,
            "avatar_url": str(user.avatar_url),
            "time_stamp": int(ctx.message.created_at.timestamp()),
            "user_id": user.id,
            "server_id": ctx.message.guild.id,
            "channel_name": ctx.channel.name,
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

        await ctx.send(f"Quote saved with id: `{ctx.message.id}`")

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
        elif isinstance(exc, commands.CommandOnCooldown):
            await ctx.send(
                f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs."
            )
        else:
            print(exc)

    @commands.command(brief="Saves a quote by reactions")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def snip(self, ctx, lines: Optional[int]):
        """
        This handy dandy command allows you to save  things your friends have said!

        lines: This argument specifies how many messages in history will be searched

        **Examples:**
            - mq>snip
            - mq>snip 150
            - Add 2 reactions to the same message, or 2 reactions to different messages (all messages in between the two reactions will be selected).

        **Note:**
            - If the selected messages contains multiple authors, it is saved as a `server snippet`.
            - If the selected messages only contain one author, it is saved as a `quote`

        Example Usage:
        https://cdn.discordapp.com/attachments/795405783155343365/816033665129250816/unknown.png
        """
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

            # reactions were not added correctly
            if reaction_one.channel_id != reaction_two.channel_id:
                await ctx.send("Reactions need to be specified in the same channel")
                return
            else:
                channel = self.bot.get_channel(reaction_one.channel_id)

            # removes reactions to provide feedback snip was taken
            message_one = await channel.fetch_message(reaction_one.message_id)
            message_two = await channel.fetch_message(reaction_two.message_id)
            await message_one.remove_reaction(reaction_one.emoji, user)
            await message_two.remove_reaction(reaction_two.emoji, user)

            msg_ids = [reaction_one.message_id, reaction_two.message_id]
            if set(msg_ids) == {reaction_one.message_id}:  # same message
                msg = await channel.fetch_message(reaction_one.message_id)
                await self.quote(ctx, msg.author, msg=msg.clean_content)
                return
            else:  # multiple messages
                messages = await channel.history(limit=lines).flatten()
                msgs = []
                snippet = False
                for indx, message in enumerate(messages):
                    if message.id in msg_ids:
                        quoted_user = message.author
                        msgs.append(message)
                        indx += 1
                        while indx < len(messages):
                            if messages[indx].author != message.author and not snippet:
                                snippet = True  # There are multiple authors in snippet
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

                if snippet:
                    snip = await self.format_snip(ctx, msgs)

                    # add snip to database
                    db.servers.update_one(
                        {"_id": ctx.guild.id}, {"$push": {"snips": snip}}
                    )

                    await ctx.send(f"Saved `server snip` with id: `{snip['snip_id']}`")
                else:
                    await self.save_snippet(ctx, quoted_user, reversed(msgs))
        except TimeoutError:
            await ctx.send("Snip timed out")

    async def format_snip(self, ctx, messages):
        messages = list(reversed(messages))
        first_msg = messages[0]
        length = len(messages)

        snip = {
            "snip_id": first_msg.id,
            "server_id": ctx.guild.id,
            "server_name": ctx.guild.name,
            "server_icon": str(ctx.guild.icon_url),
            "channel_name": first_msg.channel.name,
            "timestamp": int(first_msg.created_at.timestamp()),
            "snipper": ctx.message.author.name,
            "public": False,
            "associated_users": [],
            "consented_users": [],
            "sections": [],
            "images": [],
        }

        indx = 0
        associated_users = set([])
        # prev_author_id = first_msg.author.id
        while indx < length:
            message = messages[indx]
            prev_author_id = message.author.id

            # represents the list of users that are snipped
            if not message.author.bot:
                associated_users.add(prev_author_id)

            section = {
                "author_name": message.author.name,
                "messages": [],
                "images": 0,
            }

            # while the same person has not finished
            while indx < length and messages[indx].author.id == prev_author_id:
                message = messages[indx]

                if message.attachments:
                    # goes through every attachment in message
                    for attachment in message.attachments:
                        # only saves if attachment is an image
                        if self.file.is_image(attachment.filename):
                            # increment # of images of this block of messages
                            section["images"] += 1
                            # add the image url to the snip
                            snip["images"].append(attachment.url)

                # adds to the section of what this person has said
                text = message.clean_content
                if text == "":
                    pass
                else:
                    section["messages"].append(text)

                # moves on to the next message
                indx += 1
                # sets the previous message's author
                prev_author_id = message.author.id

            # adds section to main snip
            snip["sections"].append(section)

        # sets the associated users
        snip["associated_users"] = list(associated_users)

        # when finished return snip
        return snip

    def new_server(self, server):
        server = {
            "_id": server.id,
            "server_name": server.name,
            "prefix": "mq>",
            "quotes_saved": 0,
            "commands_invoked": 0,
            "ignored": [],
            "allowed": [],
            "whitelist": False,
            "blacklist": False,
            "del_on_save": False,
            "snips": [],
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

    # deletes commands on save
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
            self.bot.cogs_ready.ready_up(self.file.file_name(__file__)[:-3])

        # gets list of commands
        self.commands = [command.name for command in self.get_commands()]


def setup(client):
    client.add_cog(Save(client))
