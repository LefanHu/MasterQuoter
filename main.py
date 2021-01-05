import discord
import random

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.content.startswith('$goodbye'):
        await message.channel.send('Bye bye!')
        return

    elif message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    elif message.content.startswith('$diceroll'):
        n = random.randint(1,6)
        await message.channel.send('You rolled a {0}!'.format(n))


client.run('enter token here')
