import datetime

# returns numbers only
def nums_only(input):
    return int("".join(i for i in input if i.isdigit()))


# IMPORT OS TO CHECK IF QUOTES.JSON EXISTS
import asyncio
import os

# environment variables
from dotenv import load_dotenv

# IMPORT DISCORD.PY. ALLOWS ACCESS TO DISCORD'S API.
import discord

# IMPORT JSON. ALLOWS FOR SAVING QUOTES
import json

# IMPORT RANDOM FOR RANDOM QUOTE
import random

# IMPORT COMMANDS FROM THE DISCORD.EXT MODULE.
from discord.ext import commands
from discord.ext.commands.bot import AutoShardedBot

# getting token from .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# print(DISCORD_TOKEN)

# SAVEFILE FOR SAVING QUOTES
save_loc = "quotes.json"

# Random variable
rand = 1
random.seed(rand)

# sets bot prefix to specified environment variable
bot = commands.Bot(command_prefix=os.getenv("COMMAND_PREFIX"))

# FUNCTION TO ADD TO JSON FILE
def write_json(data, filename=save_loc):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


# ON READY
@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


# Ping bot for prefix
@bot.event
async def on_message(ctx):
    mention = f"<@!{bot.user.id}>"
    if mention in ctx.content:
        await ctx.channel.send(
            """The prefix of the bot is '{}'""".format(os.getenv("COMMAND_PREFIX"))
        )


# Prefix changer
@bot.command()
async def setprefix(ctx, prefix):
    bot.command_prefix = prefix
    await ctx.send(f"Prefix changed to ``{prefix}``")


# TEST BOT COMMANDS
@bot.command()
async def ping(ctx):
    await ctx.channel.send("pong")


# Quoting last message from specified user
@bot.command()
async def qlast(ctx, user: discord.Member, prev=0):
    # if user quotes themselves, quote one message further back
    if (ctx.message.author.id) == user.id:
        prev += 1

    # stores last 100 messages in channel where it is called in list
    messages = await ctx.channel.history(limit=100).flatten()

    # messages from user specified within last 100 messages
    msgs_from_user = []
    for message in messages:
        if message.author.id == user.id:

            msgs_from_user.append(message)

    # if not within last 100 messages, deal with issue, otherwise... save quote
    if not msgs_from_user:
        ctx.send("No messages from specified user was found in the last 100 messages.")
        return
    elif prev > len(msgs_from_user) - 1:
        ctx.send(
            "The most recent #{}th message was not found in the last 100 messages."
        )
        return
    else:
        #Date of message in UTC
        messageDate = msgs_from_user[prev].created_at.strftime("%m/%d/%Y, %H:%M:%S UTC")
        
        await save(ctx, user, msgs_from_user[prev].content)


# Finding the last 10 lines a user had said
@bot.command()
async def qhistory(ctx, user: discord.Member):

    # Stores last 100 messages in channel where it is called in list
    messages = await ctx.history(limit=100).flatten()

    # Prints out the specific user's messages in the last 10 messages
    output = ""
    for message in messages:
        if message.author.id == user.id:
            output = output + message.content + "\n"

    # if there is no messages from specified user in the last 100 lines
    if output == None:
        await ctx.send(
            "There is no messages from the specified user in the last 100 messages in this channel."
        )
        return

    # send output to channel
    # TODO: "remember to deal with message limit of discord"
    await ctx.send(output)


# adding new server
def add_server(server_id):
    # add new server id
    print("server added")


# testing saving quotes
@bot.command()
async def save(ctx, user: discord.Member, msg):
    data = {"userid": user.id, "msg": "<{}> ".format(user.display_name) + msg}
    server_id = ctx.message.guild.id

    if os.path.isfile("quotes.json") and os.path.getsize("quotes.json") > 0:
        with open(save_loc) as json_file:
            file = json.load(json_file)
            temp = file[server_id]["quotes"]
            temp.append(data)
        write_json(file)

    else:
        await ctx.send("First time use, there are no quotes.")
        data = {}
        data[server_id]["quotes"] = []
        data[server_id]["quotes"].append(
            {"userid": user.id, "msg": "<{}> ".format(user.display_name) + msg}
        )
        # writing to file
        write_json(data)
    await ctx.send("Quote saved...")


# temp for creators
@bot.command()
async def tempreset(ctx):
    if ctx.message.author.id in os.getenv("DEVELOPERS"):
        open("quotes.json", "w").close()
        await ctx.send("Quotes file has been cleared.")
    else:
        await ctx.send("You do not have the permissions to clear the quotes file. ")


# Outputting every single quote
@bot.command()
async def qall(ctx):
    with open(save_loc) as json_file:
        data = json.load(json_file)
        messages = data["quotes"]

        # Outputting all the quotes as one single string
        # ENSURE THIS DOESN'T EXCEED DISCORD MESSAGE LIMIT
        output = "All Quotes Listed Below: \n"
        
        for message in messages:
            output = output + ("%s \n\n" % (message["msg"]))

    #Ensuring the discord message limit is not reached
    if len(output) > 1900:
        await ctx.send("Quote word limit reached.")
    else:
        await ctx.send(output)


# Outputting all quotes of a specific user
@bot.command()
async def qlist(ctx, user: discord.Member):
    output = ""
    with open(save_loc) as json_file:
        data = json.load(json_file)
        for quote in data["quotes"]:
            if user.id == quote["userid"]:
                output = output + ("%s \n" % (quote["msg"]))

    # if there are no quotes from specified user
    if not output:
        await ctx.send("There are no quotes from this user")
    else:
        await ctx.send(output)


# CHOOSING RANDOM QUOTE AND SENDING
@bot.command()
async def qrand(ctx):
    quote_arr = []
    with open(save_loc) as json_file:
        data = json.load(json_file)
        for quote in data["quotes"]:
            quote_arr.append(quote["msg"])
    await ctx.send(random.choice(quote_arr))


# Choosing a random quote from a user
@bot.command()
async def quser(ctx, user: discord.Member):
    quote_arr = []
    with open(save_loc) as json_file:
        data = json.load(json_file)
        for quote in data["quotes"]:
            if user.id == quote["userid"]:
                quote_arr.append(quote["msg"])
    await ctx.send(random.choice(quote_arr))


# sends id of mentioned user
@bot.command(name="id")
async def id_(ctx, user: discord.Member):
    await ctx.send(user.id)


# Quotes last 100 messages (Just a tester)
@bot.command()
async def quote_last_hundred(ctx):
    messages = await ctx.channel.history(limit=100).flatten()
    for message in messages:
        await save(ctx, message.author, message.content)


# Fun little guessing game
@bot.command()
async def qguess(ctx):
    with open(save_loc) as json_file:
        data = json.load(json_file)
        quotes = data["quotes"]

    # selecting the random quote
    quote_selected = random.choice(quotes)
    answerid = quote_selected["userid"]

    await ctx.send(quote_selected["msg"])
    await ctx.send("Guess whose quote this is! ")

    guess = 2  # random false guess
    try:
        guess = await bot.wait_for("msg", timeout=30)
        guessid = nums_only(guess.content)
    except asyncio.TimeoutError:
        # prevent always waiting for user input
        ctx.send("You have run out of time to guess.")
        return

    if guessid == answerid:
        await ctx.send(
            "You are right! It was indeed {}".format(
                bot.get_user(answerid).display_name
            )
        )
    else:
        await ctx.send("You guessed: {}\nBut it was: {}".format(guessid, answerid))


# serves as an embed test as well as a self description for bot
@bot.command()
async def about(ctx):
    embed = discord.Embed(
        title="MasterQuoter is now ready!",
        colour=discord.Colour(0xFAAB3F),
        url="https://discordapp.com",
        description="MasterQuoter is a bot made by team 'MasterBaiters' designed to save and snip all the best quotes made by your friends. A great addition to any lively discord server.\n\nPlease support our patreon [here](https://github.com/LefanHu/MasterQuoter).",
        timestamp=datetime.datetime.utcfromtimestamp(1610925790),
    )

    embed.set_thumbnail(
        url="https://ih1.redbubble.net/image.683731832.0708/flat,750x1000,075,f.u6.jpg"
    )
    embed.set_author(
        name="Master Quoter",
        url="https://discordapp.com",
        icon_url="https://cdn.discordapp.com/embed/avatars/0.png",
    )
    embed.set_footer(
        text="MasterQuoter", icon_url="https://cdn.discordapp.com/embed/avatars/0.png"
    )

    embed.add_field(name="<3", value="We hope you enjoy this bot...")

    await ctx.send(embed=embed)


# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run(DISCORD_TOKEN)
