import discord
from discord.ext import commands
import sqlite3
from sqlite3 import Error

sqlpath = "quotes.db"
bot = commands.Bot(command_prefix='$')

#used for stripping characters from discord userids
#example found here https://stackoverflow.com/questions/17336943/removing-non-numeric-characters-from-a-string
import re
def get_nums(string):
    result = re.sub('[^0-9]','', string)
    return type(int(result))

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

@bot.command()
async def test(ctx):
    await ctx.channel.send("test complete")

#work in progress, currently not working
@bot.command()
async def save(ctx, user, message):
    conn = create_connection(sqlpath)
    
    #creating cursor for selection in sql
    c = conn.cursor()
    #checking if table exists
    sql = "SELECT name FROM sqlite_master WHERE type='table' AND name='{quotes}'"
    if (c.execute(sql) == False):
        ctx.send("The table does not exist, attempting to create one...")
        #create table here
        try:
            #attempting to create table in sql database
            c.execute('''CREATE TABLE quotes (userid, date, message)''')
        except Error as e:
            ctx.send(f"The error '{e}' occurred")    
    else:
        ctx.send("The table exists already. Saving quote.")
        #saving the quote
        try:
            c.execute("INSERT INTO quotes VALUES (?, ?, ?)", user, message, date)
        except Error as e:
            ctx.send(f"The error '{e}' occurred")

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command()
async def hello2(ctx, args):
    ctx.send(args)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith('$return '):
        #splitting message
        string = message.content.split()
        print('USERID = {0}'.format(string[1]))
        return
        

#running the bot
bot.run('Nzk1NzU2ODMyMTY0NDEzNTAw.X_OATQ.bT2htac4jJ_ygYxxHWUHlHNAuOU')