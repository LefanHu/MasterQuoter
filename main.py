# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord

# IMPORT JSON. ALLOWS FOR SAVING QUOTES
import json

# IMPORT COMMANDS FROM THE DISCORD.EXT MODULE.
from discord.ext import commands

#getting token from file "token.txt"
def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()
DISCORD_TOKEN = read_token()

#used for stripping characters from discord userids
#example found here https://stackoverflow.com/questions/17336943/removing-non-numeric-characters-from-a-string
import re
def get_nums(string):
    result = re.sub('[^0-9]','', string)
    return type(int(result))

#SAVEFILE FOR SAVING QUOTES
save_loc = "quotes.json"

# CREATES A NEW BOT OBJECT WITH A SPECIFIED PREFIX. IT CAN BE WHATEVER YOU WANT IT TO BE.
bot = commands.Bot(command_prefix="$")

# ON READY
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

# TEST BOT COMMANDS
@bot.command()
async def ping(ctx):
	await ctx.channel.send("pong")

#testing saving quotes
@bot.command()
async def save(ctx, userid, message):
    data = {}
    data['quotes'] = []
    data['quotes'].append({
        'userid': userid,
        'message': message
    })

    #saving to file
    with open(save_loc, 'w') as outfile:
        json.dump(data, outfile)
    
    await ctx.channel.send ("Quote saved...")

@bot.command()
async def qlist(ctx):
    with open(save_loc) as json_file:
        data = json.load(json_file)
        for quote in data['quotes']:
            await ctx.channel.send('USERID: ' + quote['userid'])
            await ctx.channel.send('MESSAGE: ' + quote['message'])

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run(DISCORD_TOKEN)