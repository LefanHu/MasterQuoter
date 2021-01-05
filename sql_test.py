import discord
from discord.ext import commands
import sqlite3
from sqlite3 import Error

client = discord.Client()
sqlpath = "quotes.db"
bot = commands.Bot(command_prefix='$')

def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

@bot.command()
async def save(ctx, user):
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

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.id == 313781087945883651:
        await message.channel.send('STFU ugly bastard, no one wants you here')
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
        return

    if message.content.startswith('$quote'):
        #splitting the message by spaces
        message.content.split()
        return
    
    if message.content.startswith('$ping '):
        #splitting th emessage by spaces
        message.content.split()
        return
    
    if message.content.startswith('$return '):
        #splitting message
        string = message.content.split()
        print('USERID = {0}'.format(string[1]))
        

#running the bot
client.run('Nzk1NzU2ODMyMTY0NDEzNTAw.X_OATQ.__1rDuwUZoDWcdKm0wwZknUOixY')