# Important
__**REMEMBER TO REMOVE .env FILE FROM GITHUB BEFORE MAKING IT PUBLIC**__

## Master Quoter (Discord bot)
Master Quoter is a quote bot made by team "Master Baiters" designed to save and snip all the best quotes made by your friends. A great addition to any lively discord server.

Work-in-progress :) (by 3 idiots in high school)

## Current TODO list
- ~~Save multiple quotes at the same time (avoids unnecessary file openings and closings)~~
- ~~Add time and date information to quotes~~
- ~~Add server id to quotes~~
- ~~Change structure in how quotes are saved~~
- ~~Add environment variables for bot token~~
- ~~Add error handling "bot.event"~~
- ~~Save attachments with message.created_at + attachment.filename instead of just attachment.filename since most of the time it's simply just "unknown.png" for screenshots~~
- ~~Send traceback to developers whenever an error occurs (currently non-working)~~
- ~~Add a buffer variable for quotes to avoid opening and closing the quotes file for every single quote.~~
- Ensure when quoting someone, message does not exceed discord limit
- Fix first time quote initialization. If quotes.json is empty but still exists, bot will not work.
- Save attachments as an actual json array instead of a json array as a string.
- Implement load from backup if reading from quotes.json errors out
- save message.clean_content instead of message.content
- Save a quote snippet through reactions

## Future plans
- ~~Implement listing quotes for specific people~~
- ~~Implement game of guessing who said the quotes~~
- ~~Embed colors for bot messages (refer below for resources)~~
- ~~Add feature to quote multiple lines from one user~~
- ~~Add attachment quoting support (ability to quote screenshots, sound files or picture attachments)~~
- ~~Add "nice navigation" (page flipping for listing quotes)~~
- Add feature to associate quote snippets with others users included in message snippet
- Comic strip or user friendly help bar OR possibly a pre-drawn image help bar


## Required Packages
- psutil [pip install psutil](https://pypi.org/project/psutil/)
- discord.py [pip install discord.py](https://pypi.org/project/discord.py/)
- python-dotenv [pip install python-dotenv](https://pypi.org/project/python-dotenv/)
- pymongo [pip install pymongo](https://pypi.org/project/pymongo/)

## Useful links
[Discord.py Documentation](https://discordpy.readthedocs.io/en/latest/)

[discord.py commands documentation](https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html)

[Markdown format Documentation](https://www.markdownguide.org/basic-syntax/)

[Function decorators in Discord.py](https://medium.com/@cantsayihave/decorators-in-discord-py-e44ce3a1aae5)

[sqlite3 database simple example](https://docs.python.org/3/library/sqlite3.html)

[Explaining @bot.command()](https://medium.com/better-programming/how-to-make-discord-bot-commands-in-python-2cae39cbfd55)

[Writing to JSON files using python-1](https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/)

[Writing to JSON file using python-2](https://www.geeksforgeeks.org/append-to-json-file-using-python/)

[Discord.py: Making a Discord bot (Part 8: Embeds)](https://www.youtube.com/watch?v=XKQWxAaRgG0)

[Getting channel id given wanted channel name](https://stackoverflow.com/questions/63321098/is-it-possible-to-get-channel-id-by-name-in-discord-py)

[discord.py decorators](https://medium.com/@cantsayihave/decorators-in-discord-py-e44ce3a1aae5)

[discord.py save attachments](https://www.reddit.com/r/Discord_Bots/comments/eojofe/py_saving_posted_images/)

[discord.py sending images, files, and other attachments](https://discordpy.readthedocs.io/en/latest/faq.html#how-do-i-upload-an-image)

[discord embed visualizer](https://leovoel.github.io/embed-visualizer/)

[environment variables for bot](https://morioh.com/p/c23c88dd2374)

[displaying multiple pages in one embed](https://stackoverflow.com/questions/63882175/making-embeds-of-more-than-one-page-using-discord-py)

[using cogs in discord.py](https://www.youtube.com/watch?v=vQw8cFfZPx0)

[check if command invoker is a user](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=check#discord.ext.commands.check)

[making a cog admin only](https://stackoverflow.com/questions/63081648/how-to-make-a-discord-py-cog-admin-only)

[very good exmample of how cogs can be used in discord.py & per server bot prefixes](https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be)

[example of a help.py cog](https://gist.github.com/OneEyedKnight/41ba697ae4284dc5b4ea15c09fb1e730)

[error handling example cog](https://gist.github.com/AileenLumina/510438b241c16a2960e9b0b014d9ed06)
