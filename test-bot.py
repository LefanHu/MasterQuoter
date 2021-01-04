import discord
import logging
import sys


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await self.change_presence(activity = discord.Game(name = "Lovely day it is today!"))

    #outputting logs to discord.log file instead of to stdout
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


    #testing the use of the discord logger
    sys.exit('Test error message hopefully to be seen in file "discord.log".')

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

client = MyClient()
client.run("Enter token here")