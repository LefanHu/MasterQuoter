import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.name == "Alex3000":
        await message.channel.send('STFU ugly bastard, no one wants you here')
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run('Enter your token here')