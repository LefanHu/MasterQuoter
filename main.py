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

    elif message.author.name == 'Alex3000' and message.content.startswith("hello"):
        await message.channel.send('Welcome Master Baiter')
        return

    elif message.author.name == 'Cuddles' and message.content.startswith("hello"):
        await message.channel.send('Welcome Master Baiter')
        return

    elif message.author.name == 'AustZW':
        await message.channel.send('Austin likes big black balls')
        return

    elif message.content.startswith('$goodbye'):
        await message.channel.send('Bye bye!')
        return

    elif message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    elif message.content.startswith('$diceroll'):
        n = random.randint(1,6)
        await message.channel.send('You rolled a {0}!'.format(n))

    elif message.content.startswith('$quote lefan'):
        lefquotes = ["my balls are huge", "i have a three milimeter defeater", "i will punish you with my one inch punisher", "alex pp is massive"]
        lefquotechoice = random.choice(lefquotes)
        await message.channel.send(lefquotechoice)


client.run('token')
