import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run('Nzk1NzU2ODMyMTY0NDEzNTAw.X_OATQ.S1JA1RSKnuHDT1YiKLe8lZQAtSk')

