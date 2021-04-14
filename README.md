# MasterQuoter (Discord bot)

Created by @Alex3000 & @Cuddles. A bot designed to save quotes.

This bot is an amazing tool to help you capture all of the funny moments, conversations, and random quotes that have happened, any time, and in any server! This bot has a number of commands that let you save quotes, display them, and keep them forvever! There are a few guessing games that you can try involving random quotes, and there are also many tools you can use to even save screenshots of hilarious conversations! We hope that you find this bot fun and useful, and we hope that it serves to liven up your discord experience!

**Invite Link:** https://discord.com/api/oauth2/authorize?client_id=795756832164413500&permissions=335936592&scope=bot

**Top.gg Bot Page:** https://top.gg/bot/795756832164413500

## Current TODO list

- ~~Save multiple quotes at the same time (avoids unnecessary file openings and closings)~~
- ~~Add time and date information to quotes~~
- ~~Add server id to quotes~~
- ~~Change structure in how quotes are saved~~
- ~~Add environment variables for bot token~~
- ~~Add error handling "bot.event"~~
- ~~Save attachments with message.created_at + attachment.filename instead of just attachment.filename since most of the time it's simply just "unknown.png" for screenshots~~
- ~~Send traceback to developers whenever an error occurs (currently non-working)~~
- ~~Ensure when quoting someone, message does not exceed discord limit~~
- ~~save message.clean_content instead of message.content~~
- ~~Save a quote snippet through reactions~~
- ~~Reporting function to notify developers of any known bugs or glitches.~~
- ~~Implement listing quotes for specific people~~
- ~~Implement game of guessing who said the quotes~~
- ~~Embed colors for bot messages (refer below for resources)~~
- ~~Add feature to quote multiple lines from one user~~
- ~~Add attachment quoting support (ability to quote screenshots, sound files or picture attachments)~~
- ~~Add "nice navigation" (page flipping for listing quotes)~~
- ~~Comic strip or user friendly help bar OR possibly a pre-drawn image help bar~~
- ~~Use mongodb for storage~~
- ~~Add feature to associate quote snippets with others users included in message snippet (not implemented yet)~~

## Future plans

- Make database queries async using 'motor' driver for mongodb
- Add ability to automatically post saved quotes & snippets to a specified channel
- Add ability to make a quote or snippet public to everyone

## Changelog

- V 1.0.0 (Initial release)
- V 1.1.0 (Added ability to save and list snips)

## Required Packages

- psutil [pip install psutil](https://pypi.org/project/psutil/)
- discord.py [pip install discord.py](https://pypi.org/project/discord.py/)
- discord.ext.menus [please see github](https://github.com/Rapptz/discord-ext-menus)
- python-dotenv [pip install python-dotenv](https://pypi.org/project/python-dotenv/)
- pymongo [pip install pymongo](https://pypi.org/project/pymongo/)
- tracemoepy [pip install tracemoe](https://pypi.org/project/tracemoepy/)
- jikanpy [pip install jikanpy](https://pypi.org/project/jikanpy/)
- nodejs [sudo apt-get install nodejs](https://tecadmin.net/install-latest-nodejs-npm-on-ubuntu/)
- ejs [npm install ejs](https://ejs.co/#docs)

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

[mongoDB documentation](https://docs.mongodb.com/manual/introduction/)

[mongodb append to list](https://stackoverflow.com/questions/33189258/append-item-to-mongodb-document-array-in-pymongo-without-re-insertion)

[mongodb updating doc from inside cursor traversal function](https://stackoverflow.com/questions/49611271/can-i-update-a-mongo-document-from-inside-a-cursor-traversal-function)

[lookup array of object ids in mongodb](https://www.tutorialspoint.com/perform-lookup-to-array-of-object-id-s-in-mongodb)

[similar to resource above](https://stackoverflow.com/questions/34967482/lookup-on-objectids-in-an-array)

[dynamically writing html code](https://www.youtube.com/watch?v=yXEesONd_54)
