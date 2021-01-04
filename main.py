import discord

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        await self.change_presence(activity = discord.Game(name = "Lovely day it is today!"))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

client = MyClient()
client.run("token")
