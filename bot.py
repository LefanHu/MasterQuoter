from asyncio import sleep

from discord import DMChannel, Embed
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import when_mentioned_or
from datetime import datetime as dt

import os
from dotenv import load_dotenv

OWNER_IDS = [324917494005366784, 313781087945883651]  # Cuddles & alex
COGS = [filename[:-3] for filename in os.listdir("./cogs") if filename.endswith(".py")]

from lib.db import db


def get_prefix(bot, message):
    try:
        prefix = db.servers.find_one({"_id": message.guild.id}, {"prefix": 1})["prefix"]
    except TypeError:  # creates server
        prefix = "mq>"
        bot.get_cog("Save").new_server(message.guild)
    return when_mentioned_or(prefix)(bot, message)


class Ready(object):
    def __init__(self):
        for cog in COGS:
            print(cog)
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        load_dotenv()

        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None
        self.permissions = 1879960784
        self.developers = OWNER_IDS

        # banlist can also go here

        super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS)

    def setup(self):
        for cog in COGS:
            self.load_extension(f"cogs.{cog}")
            print(f" {cog} cog loaded")

        print("setup complete")

    def run(self, version):
        self.VERSION = version

        print("running setup...")
        self.setup()

        self.TOKEN = os.getenv("DISCORD_TOKEN")  # DISCORD_TOKEN

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            # prevent those on banlist to be here.
            if not self.ready:
                await ctx.send(
                    "I'm not ready to receive commands. Please wait a few seconds."
                )
            elif (
                message.author.id
                in db.servers.find_one({"_id": ctx.guild.id}, {"ignored": 1})["ignored"]
            ):
                await ctx.send("You've been ignored on this server")
            else:
                await self.invoke(ctx)

    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(795405783155343361)
            self.stdout = self.get_channel(795405783155343365)

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            print("Now online!")
            self.ready = True
            print("bot ready")

            # perhaps deal with bot's status here

        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            if isinstance(message.channel, DMChannel):
                msg = message.clean_content
                embed = Embed(timestamp=dt.utcnow(), colour=0x00FFFF)
                embed.add_field(name="FROM:", value=f"From: {message.author}")
                embed.add_field(name="REPORT", value=f"Msg: {msg}", inline=False)

                for attachment in message.attachments:
                    img = attachment.url
                    embed.set_image(url=img)
                # Sends the error to direct messages

                cog_error = self.get_cog("Error")

                for developer in self.developers:
                    user = await self.fetch_user(developer)

                    await cog_error.dm(user, embed)

                await message.channel.send(
                    "Thanks! Your message has been relayed to the developers"
                )
            else:
                await self.process_commands(message)


bot = Bot()

bot.run("0.0.1 BETA")