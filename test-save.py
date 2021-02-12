import datetime
from random import random

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


# supported image saving types
image_types = ["png", "jpeg", "gif", "jpg"]


# ON READY
@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


# TEST BOT CONNECTED
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
        await ctx.send(
            "No messages from specified user was found in the last 100 messages."
        )
        return
    elif prev > len(msgs_from_user) - 1:
        await ctx.send(
            "The most recent #{}th message was not found in the last 100 messages."
        )
        return
    else:
        await save(ctx, user, msgs_from_user[prev].content)


async def save_attachments(ctx):
    attachments = []
    for attachment in ctx.message.attachments:
        if any(attachment.filename.lower().endswith(image) for image in image_types):
            await attachment.save(attachment.filename)
            image_name = str(ctx.message.created_at) + attachment.filename
            attachments.append(image_name)

    for name in attachments:
        if name == "":
            await ctx.send("An error has occured, the image was not saved")

    # await ctx.send("Your image has been saved as {}\n\nWas this your image?".format(image_name))
    return json.dumps(attachments)
    # await ctx.send(file=discord.File(image_name))


# testing saving quotes
@bot.command()
async def save(ctx, user: discord.Member, msg):
    quote = {
        "msg": msg,
        "display_name": user.display_name,
        "time": "{}".format(ctx.message.created_at.strftime("%m/%d/%Y, %H:%M:%S")),
        "attachments": await save_attachments(ctx),
    }
    server_id = str(ctx.message.guild.id)
    mem_id = str(user.id)

    # checking if file exists
    if os.path.isfile(save_loc) and os.path.getsize(save_loc) > 0:
        with open(save_loc) as json_file:
            file = json.load(json_file)

            if server_id not in file:  # server has not used bot
                print("server id does not exist")
                qt = {}
                qt["quotes"] = [quote]

                member = {}
                member[mem_id] = qt

                server = {}
                server[server_id] = member

                file.update(server)

            elif mem_id not in file[server_id]:  # member has not been quoted
                print("server id exists, userid does not")

                qt = {}
                qt["quotes"] = [quote]

                member = {}
                member[mem_id] = qt

                file[server_id].update(member)
            else:  # adding another quote to user
                print("server id & member id exists")
                file[server_id][mem_id]["quotes"].append(quote)

        write_json(file)
    else:  # this is for first time use of bot
        qt = {}
        qt["quotes"] = [quote]

        member = {}
        member[mem_id] = qt

        file = {}
        file[server_id] = member

        # writing to file
        write_json(file)

    await ctx.send("Quote saved...")


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
        members = data[str(ctx.message.guild.id)]

    # selecting the random quote
    random_member = random.choice(list(members))  # converts members into a list
    quote_selected = random.choice(members[random_member]["quotes"])

    # answer is the chosen member's quote
    answerid = random_member

    await ctx.send(quote_selected["msg"])
    await ctx.send("Guess whose quote this is! ")

    guess = 2  # random false guess
    try:
        guess = await bot.wait_for("msg", timeout=30)
        guessid = nums_only(guess.content)
    except asyncio.TimeoutError:
        # prevent always waiting for user input
        await ctx.send("You have run out of time to guess.")
        return

    if guessid == answerid:
        await ctx.send(
            "You are right! It was indeed {}".format(
                bot.get_user(answerid).display_name
            )
        )
    else:
        await ctx.send("You guessed: {}\nBut it was: {}".format(guessid, answerid))


# Prefix changer
@bot.command()
async def setprefix(ctx, prefix):
    bot.command_prefix = prefix
    await ctx.send(f"Prefix changed to ``{prefix}``")


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
