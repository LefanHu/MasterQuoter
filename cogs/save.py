from re import I
import discord
from discord.ext import commands, tasks
import json
from lib.file_utils import File
from typing import Optional
from asyncio import TimeoutError


class Save(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.image_types = ["png", "jpeg", "gif", "jpg"]
        self.file = File()
        self.save_location = self.file.getenv("SAVE_LOCATION")
        self.DEVELOPERS = self.file.getenv("DEVELOPERS")

        self.quote_buffer = []
        self.delete_buffer = []
        self.update_quotes.start()

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
            await self.append_quote(ctx=ctx, user=message.author, msg=message.content)

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

    @commands.command(aliases=["qlast", "ql"], brief="Quotes the last thing someone said")
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

        await self.append_quote(ctx, user, msg=msgs, imgs=imgs, files=files)

    # this is here so append_quote's extra parameters don't show up in help
    @commands.command(aliases=["qt"])
    async def quote(self, ctx, user: discord.Member, *, msg):
        """This handy dandy command allows you to save  things your friends have said!"""
        await self.append_quote(ctx, user, msg=msg)

    # Adds one quote to quote buffer

    async def append_quote(self, ctx, user: discord.Member, *, msg, imgs=[], files=[]):
        quote = {
            "msg": msg,
            "name": str(user),
            "display_name": user.display_name,
            "user_id": user.id,
            "avatar_url": str(user.avatar_url),
            "time_stamp": int(ctx.message.created_at.timestamp()),
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
        server_id = ctx.message.guild.id
        mem_id = user.id

        # save info to array
        array = [server_id, mem_id, quote]

        # adds the qutoe to the buffer
        self.quote_buffer.append(array)

    @quote.error
    async def quote_error(self, ctx, exc):
        if isinstance(exc, commands.MissingRequiredArgument):
            if not ctx.message.attachments:
                await ctx.send("Quote cannot be empty.")
            else:
                imgs = await self.save_images(ctx.message)
                await self.append_quote(ctx, ctx.message.mentions[0], msg="", imgs=imgs)
        elif isinstance(exc, commands.MemberNotFound):
            await ctx.send("That member cannot be found.")

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

    def new_server(self, guild_id):
        guild = self.bot.get_guild(int(guild_id))
        server = {
            "guild_name": guild.name,
            "guild_id": guild.id,
            "icon_url": str(guild.icon_url),
            "quoted_members": [],
            "members": [],
        }

        return server

    def new_member(self, user_id, quote=None):
        user = {"user_id": user_id, "quotes": []}

        if not not quote:
            user["quotes"].append(quote)

        return user

    # def remove_quotes(self, server, user, file):
    #     for guild_indx, guild in enumerate(file["guilds"]):
    #         if guild["guild_id"] == server["guild_id"]:
    #             target_guild = guild_indx
    #     target_member = None
    #     for member_indx, member in enumerate(file["guilds"][target_guild]["members"]):
    #         if member["user_id"] == user["user_id"]:
    #             target_member = member_indx

    #     if not target_member:
    #         file["guilds"][target_guild]["members"].append(user)
    #     else:
    #         file["guilds"][target_guild]["members"][target_member]["quotes"] = user[
    #             "quotes"
    #         ]

    #     return file

    @commands.command(aliases=["rm", "remove"])
    async def remove_quote(self, ctx, quote_id):
        self.delete_buffer.append([ctx.message.guild.id, int(quote_id)])

    # Clears buffer
    @tasks.loop(seconds=2.0)
    async def update_quotes(self):
        # print(self.quote_buffer)

        # If file doesn't exist, create one
        if self.file.exists(self.save_location):
            with open(self.save_location) as json_file:
                file = json.load(json_file)
        else:  # create new file
            file = {"guilds": []}
            self.file.write_json(file, self.save_location)

        # saving quotes
        for quote in self.quote_buffer:
            guild_id, user_id, quote = quote

            server = self.file.get_server(guild_id, file)
            member = self.file.get_member(user_id, server)

            if not server:
                # server will always exist
                file["guilds"].append(self.new_server(guild_id))
                server = self.file.get_server(guild_id, file)
                # print(f"{file['guilds']} \n\n{server}")
                member = self.new_member(user_id, quote)
                server["members"].append(member)
                server["quoted_members"].append(member["user_id"])
            elif not member:
                member = self.new_member(user_id, quote)
                server["members"].append(member)
                server["quoted_members"].append(member["user_id"])
            else:
                member["quotes"].append(quote)

        # deleting quotes
        try:
            guild_ids, del_quote_ids = zip(*self.delete_buffer)

            for guild_id in guild_ids:
                server = self.file.get_server(guild_id, file)
                for member in server["members"]:
                    for quote in member["quotes"]:
                        if quote["message_id"] in del_quote_ids:
                            member["quotes"].remove(quote)

                            # remove member if no quotes are left
                            if len(member["quotes"]) == 0:
                                server["quoted_members"].remove(member["user_id"])
                                server["members"].remove(member)
        except ValueError:
            pass

        # skip if there's no quotes to save
        if not self.quote_buffer and not self.delete_buffer:
            pass
        else:
            self.file.write_json(file, self.save_location)
            self.quote_buffer.clear()
            self.delete_buffer.clear()

    @update_quotes.before_loop
    async def before_update_quotes(self):
        await self.bot.wait_until_ready()

    @update_quotes.after_loop
    async def after_update_quotes(self):
        if len(self.quote_buffer) + len(self.delete_buffer) > 0:
            await self.update_quotes()
        print("Quote buffers cleared")


def setup(client):
    client.add_cog(Save(client))
    print(f"Cog '{File().file_name(__file__)}' has been loaded")
