from re import I
import discord
from discord.ext import commands, tasks
import json
from lib.file_utils import File
from typing import Optional


class Save(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.image_types = ["png", "jpeg", "gif", "jpg"]
        self.file = File()
        self.save_location = self.file.getenv("SAVE_LOCATION")
        self.save_quotes.start()
        self.quote_buffer = []

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
    async def quote_last(self, ctx, user: discord.Member, lines: Optional[int]):
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
        attachments = {}
        for message in messages:
            msgs.append(message.clean_content)
            attachments.update(await self.save_attachments(message))

        await self.append_quote(ctx, user, msg=msgs, attachments=attachments)

    # Adds one quote to quote buffer
    @commands.command(aliases=["quote"])
    async def append_quote(self, ctx, user: discord.Member, *, msg):
        """This handy dandy command allows you to save  things your friends have said!"""

        quote = {
            "msg": msg,
            "name": str(user),
            "display_name": user.display_name,
            "user_id": user.id,
            "avatar_url": str(user.avatar_url),
            "snippet": True if type(msg) == list else False,
            "time_stamp": int(ctx.message.created_at.timestamp()),
            "server": ctx.message.guild.name,
            "server_id": ctx.message.guild.id,
            "channel": ctx.message.channel.name,
            "channel_id": ctx.message.channel.id,
            "message_id": ctx.message.id,
            "image_attachments": await self.save_images(ctx.message),
            "attachments": await self.save_attachments(ctx.message),
        }
        server_id = str(ctx.message.guild.id)
        mem_id = str(user.id)

        # save info to array
        array = [server_id, mem_id, quote]

        # adds the qutoe to the buffer
        self.quote_buffer.append(array)

    @append_quote.error
    async def append_quote_error(self, ctx, exc):
        if isinstance(exc, commands.MissingRequiredArgument):
            if not ctx.message.attachments and not ctx.message.mentions:
                await ctx.send("Quote cannot be empty.")
            else:
                self.append_quote(
                    ctx, ctx.message.mentions[0], ctx.message.clean_content
                )
        elif isinstance(exc, commands.MemberNotFound):
            await ctx.send("That member cannot be found.")

    # Clears buffer
    @tasks.loop(seconds=2.0)
    async def save_quotes(self, quote_list=None):
        save_location = self.save_location

        # Default quote list
        if quote_list is None:
            quote_list = self.quote_buffer

        # If file doesn't exist, create one
        if self.file.exists(save_location):
            pass
        else:  # create new file
            template_file = self.file.getenv("TEMPLATE_FILE")
            with open(template_file) as json_file:
                file = json.load(json_file)
                self.file.write_json(file, save_location)

        if not quote_list:
            pass
        else:
            with open(save_location) as json_file:
                file = json.load(json_file)

                for quote in quote_list:
                    server_id = quote[0]
                    mem_id = quote[1]
                    quote = quote[2]

                    if server_id not in file:  # server has not used bot
                        # print("server id does not exist")
                        qt = {}
                        qt["quotes"] = [quote]

                        member = {}
                        member[mem_id] = qt

                        server = {}
                        server[server_id] = member

                        file.update(server)

                    elif mem_id not in file[server_id]:  # member has not been quoted
                        # print("server id exists, userid does not")

                        qt = {}
                        qt["quotes"] = [quote]

                        member = {}
                        member[mem_id] = qt

                        file[server_id].update(member)
                    else:  # adding another quote to user
                        # print("server id & member id exists")
                        file[server_id][mem_id]["quotes"].append(quote)
            self.file.write_json(file, save_location)
            self.quote_buffer.clear()


def setup(client):
    client.add_cog(Save(client))
    print(f"Cog '{File().file_name(__file__)}' has been loaded")
