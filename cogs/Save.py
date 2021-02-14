import discord
from discord.ext import commands, tasks
import json
from cogs.file_utils import File


class Save(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.image_types = ["png", "jpeg", "gif", "jpg"]
        self.save_location = File(self.client).get_env("SAVE_LOCATION")
        save = self.save_quotes.start()

        self.quote_buffer = []

    # getting a sample dataset
    @commands.command(aliases=["slh"])
    async def save_last_hundred(self, ctx):
        messages = await ctx.channel.history(limit=100).flatten()
        for message in messages:
            await self.quote(ctx=ctx, user=message.author, msg=message.content)

    # Saving attachments associated with a message
    async def save_attachments(self, message):
        attachments = []
        for attachment in message.attachments:
            if any(
                attachment.filename.lower().endswith(image)
                for image in self.image_types
            ):
                image_name = str(message.created_at) + attachment.filename
                await attachment.save(attachment.filename)
                attachments.append(image_name)
        return json.dumps(attachments)

    # Adds one quote to quote buffer
    @commands.command()
    async def quote(self, ctx, user: discord.Member, *, msg):
        quote = {
            "msg": msg,
            "display_name": user.display_name,
            "time": "{}".format(ctx.message.created_at.strftime("%m/%d/%Y, %H:%M:%S")),
            "attachments": await self.save_attachments(ctx.message),
            "channel": ctx.message.channel.name,
        }
        server_id = str(ctx.message.guild.id)
        mem_id = str(user.id)

        # save info to array
        array = [server_id, mem_id, quote]

        # adds the qutoe to the buffer
        self.quote_buffer.append(array)

    # Clears buffer
    @tasks.loop(seconds=2.0)
    async def save_quotes(self, quote_list=None):
        save_location = self.save_location

        # Default quote list
        if quote_list is None:
            quote_list = self.quote_buffer

        # If file doesn't exist, create one
        if File(self.client).file_exists(save_location):
            pass
        else:  # create new file
            template_file = File(self.client).get_env("TEMPLATE_FILE")
            with open(template_file) as json_file:
                file = json.load(json_file)
                File(self.client).write_json(file, save_location)

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
            File(self.client).write_json(file, save_location)
            self.quote_buffer.clear()


def setup(client):
    client.add_cog(Save(client))
    print(f"Cog '{File(client).file_name(__file__)}' has been loaded")