import discord
from discord.ext import commands, tasks
import json


class Save(commands.Cog):
    quote_buffer = []

    def __init__(self, client):
        self.client = client
        self.image_types = ["png", "jpeg", "gif", "jpg"]

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
            "attachments": await self.save_attachments(self, ctx.message),
        }
        server_id = str(ctx.message.guild.id)
        mem_id = str(user.id)

        # save info to array
        array = [server_id, mem_id, quote]

        # adds the qutoe to the buffer
        Save.quote_buffer.append(array)

    # Clears buffer
    @tasks.loop(seconds=2)
    def save_quotes(self, ctx, quote_list=None):
        get_env = self.bot.get_command("get_env")
        save_location = ctx.invoke(get_env("SAVE_LOCATION"))

        if quote_list is None:
            quote_list = Save.quote_buffer

        if not quote_list:
            pass
        else:
            for quote in quote_list:
                server_id = quote[0]
                mem_id = quote[1]
                quote = quote[2]


def setup(client):
    client.add_cog(Save(client))
    print(f"Cog 'Saving' has been loaded")