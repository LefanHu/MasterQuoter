# IMPORT OS TO CHECK IF QUOTES.JSON EXISTS
import os.path

# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord

# IMPORT JSON. ALLOWS FOR SAVING QUOTES
import json

# IMPORT RANDOM FOR RANDOM QUOTE
import random

# IMPORT COMMANDS FROM THE DISCORD.EXT MODULE.
from discord.ext import commands
from discord.ext.commands.bot import AutoShardedBot

#getting token from file "token.txt"
def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()
DISCORD_TOKEN = read_token()

#SAVEFILE FOR SAVING QUOTES
save_loc = "quotes.json"

# CREATES A NEW BOT OBJECT WITH A SPECIFIED PREFIX. IT CAN BE WHATEVER YOU WANT IT TO BE.
bot = commands.Bot(command_prefix="$")

# FUNCTION TO ADD TO JSON FILE
def write_json(data, filename = save_loc):
    with open(filename, 'w') as f:
        json.dump(data, f, indent = 4)

# ON READY
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

# TEST BOT COMMANDS
@bot.command()
async def ping(ctx):
	await ctx.channel.send("pong")

#Quoting last message from specified user
@bot.command()
async def qlast(ctx, user: discord.Member, prev = 0):
    #if user specified how many messages back, adjust numbers to make more sense
    if prev > 0:
        prev-=0

    elif (ctx.message.author.id)==user.id:
        prev+=1


    #stores last 100 messages in channel where it is called in list
    messages = await ctx.channel.history(limit=100).flatten()

    #messages from user specified within last 100 messages
    msgs_from_user = []
    for message in messages:

        if message.author.id == user.id:

            msgs_from_user.append(message)

    #if not within last 100 messages, deal with issue, otherwise... save quote
    if not msgs_from_user:
        ctx.send("No messages from specified user was found in the last 100 messages.")
        return
    elif prev > len(msgs_from_user) - 1:
        ctx.send("The most recent #{}th message was not found in the last 100 messages.")
        return
    else:
        await save(ctx, user, msgs_from_user[prev].content)

#testing saving quotes
@bot.command()
async def save(ctx, user: discord.Member, message):
    data = {
        "userid":user.id,
        "message": '<{}> '.format(user.display_name) + message
    }

    if os.path.isfile('quotes.json'):
        with open(save_loc) as json_file:
            file = json.load(json_file)
            temp = file['quotes']
            temp.append(data)
        write_json(file)
    else:
        await ctx.send("First time use, there are no quotes.")
        data = {}
        data['quotes'] = []
        data['quotes'].append({
            'userid': user.id,
            'message': '<{}> '.format(user.display_name) + message
        })
        #writing to file
        write_json(data)
    await ctx.send ("Quote saved...")

@bot.command()
async def qall(ctx):
    with open(save_loc) as json_file:
        data = json.load(json_file)
        messages = data['quotes']

        # Outputting all the quotes as one single string
        # ENSURE THIS DOESN'T EXCEED DISCORD MESSAGE LIMIT
        output = 'All Quotes Listed Below: \n'
        for message in messages:
            output = output + ('%s \n\n' % (message['message']))

    await ctx.send(output)

@bot.command()
async def qlist(ctx, user):
    with open(save_loc) as json_file:
        data = json.load(json_file)
        for quote in data ['quotes']:
            if(user == quote['userid']):
                await ctx.send('MESSAGE: ' + quote['message'])


# CHOOSING RANDOM QUOTE AND SENDING
@bot.command()
async def qrand(ctx):
    quote_arr = []
    with open(save_loc) as json_file:
        data = json.load(json_file)
        for quote in data['quotes']:
            quote_arr.append(quote['message'])
    await ctx.send(random.choice(quote_arr))

@bot.command()
async def quser(ctx, user:discord.Member):
    quote_arr = []
    with open(save_loc) as json_file:
        data = json.load(json_file)
        for quote in data['quotes']:
            if(user.id == quote['userid']):
                quote_arr.append(quote['message'])
    await ctx.send(random.choice(quote_arr))

@bot.command()
async def qguess(ctx):
    quote_arr = []
    with open(save_loc) as json_file:
        data = json.load(json_file)
        for quote in data['quotes']:
            quote_arr.append(quote['message'])
    await ctx.send(random.choice(quote_arr))
    await ctx.send('Guess whose quote this is! ')



# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run(DISCORD_TOKEN)
