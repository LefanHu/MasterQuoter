import enum
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
        self.quote_buffer = []
        self.delete_buffer = []
        self.update_quotes.start()

    def is_owner(self, ctx):
        print(ctx.message.author in self.file.get_env("DEVELOPERS"))
        return ctx.message.author in self.file.get_env("DEVELOPERS")

    # getting a sample dataset
    @commands.command(aliases=["slh"])
    @commands.is_owner()
    async def save_last_hundred(self, ctx):
        """This command lets you save THE LAST HUNDRED quotes!\n"""

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

    @commands.command(aliases=["qlast"])
    async def quote_last(
        self, ctx, user: discord.Member, section: Optional[int], lines: Optional[int]
    ):
        if lines is None or lines > 200:
            lines = 100

        messages = await ctx.channel.history(limit=lines).flatten()

        msgs = []
        found_user = False
        for indx, message in enumerate(messages):
            if indx == 0 and message.author.id == user.id:
                pass
            elif found_user and message.author.id != user.id:
                break
            elif message.author.id == user.id:
                found_user = True
                msgs.append(message)

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
                self.append_quote(
                    ctx, ctx.message.mentions[0], msg=ctx.message.clean_content
                )
        elif isinstance(exc, commands.MemberNotFound):
            await ctx.send("That member cannot be found.")

    # @commands.command()
    # async def snip(self, ctx, emoji: str):
    #     user = ctx.author

    #     def is_correct(reaction, user):
    #         print(reaction.event_type)

    #         # return (
    #         #     reaction.message.author.id == user.id
    #         #     and reaction.message.id == ctx.message.id
    #         # )

    #     try:
    #         reaction = await self.bot.wait_for(
    #             "reaction_add", check=is_correct, timeout=60.0
    #         )
    #         print(type(reaction))

    #     except TimeoutError:
    #         await ctx.send("Snip timed out")

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

    def remove_quotes(self, server, user, file):
        for guild_indx, guild in enumerate(file["guilds"]):
            if guild["guild_id"] == server["guild_id"]:
                target_guild = guild_indx
        target_member = None
        for member_indx, member in enumerate(file["guilds"][target_guild]["members"]):
            if member["user_id"] == user["user_id"]:
                target_member = member_indx

        if not target_member:
            file["guilds"][target_guild]["members"].append(user)
        else:
            file["guilds"][target_guild]["members"][target_member]["quotes"] = user[
                "quotes"
            ]

        return file

    @commands.command(aliases=["rm", "remove"])
    async def remove_quote(self, ctx, quote_id):
        self.delete_buffer.append([ctx.message.guild.id, int(quote_id)])

    # Clears buffer
    @tasks.loop(seconds=2.0)
    async def update_quotes(self):
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
