import asyncio
import discord

# IMPORT COMMANDS FROM THE DISCORD.EXT MODULE.
from discord.ext import commands

#reading bot token frome file
def read_token():
    with open("token.txt", "r") as f:
        lines = f.readlines()
        return lines[0].strip()
DISCORD_TOKEN = read_token()

#bot command prefix
bot = commands.Bot(command_prefix="$")

image_types = ["png", "jpeg", "gif", "jpg"]

#simple 
@bot.event
async def on_message(message: discord.Message):
    #ignore self
    if message.author == bot.user:
        return

    ctx = await bot.get_context(message)
    image_name = ""
    for attachment in message.attachments:
        if any(attachment.filename.lower().endswith(image) for image in image_types):
            await attachment.save(attachment.filename)
            image_name = attachment.filename

    if image_name == "":
        ctx.send("An error has occured, the image was not saved")
    else:    
        await ctx.send("Your image has been saved as {}\n\nWas this your image?".format(image_name))
        await ctx.send(file=discord.File(image_name))

@bot.event
async def on_ready():
    print("connected")

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN. TOKEN HAS BEEN REMOVED AND USED JUST AS AN EXAMPLE.
bot.run(DISCORD_TOKEN)