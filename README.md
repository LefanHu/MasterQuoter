# Important
__**REMEMBER TO REMOVE .env FILE FROM GITHUB BEFORE MAKING IT PUBLIC**__

## Master Quoter (Discord bot)
Master Quoter is a quote bot made by team "Master Baiters" designed to save and snip all the best quotes made by your friends. A great addition to any lively discord server.

Work-in-progress :) (by 2 idiots in high school)

## Current TODO list
- If quotes of one user exceed a total of 2000 characters, command !qlist @user will crash due to discord message limit
- Save multiple quotes at the same time (avoids unnecessary file openings and closings)
- Add time and date information to quotes
- Add server id to quotes
- Change structure in how quotes are saved
- Add environment variables for bot token
- Add error handling "bot.event"
- Fix first time quote initialization. If quotes.json is empty but still exists, bot will not work.
- Add a buffer variable for quotes to avoid opening and closing the quotes file for every single quote.
- Save attachments as an actual json array instead of a json array as a string.
- ~~Save attachments with message.created_at + attachment.filename instead of just attachment.filename since most of the time it's simply just "unknown.png" for screenshots~~

## Future plans
- ~~Implement listing quotes for specific people~~
- ~~Implement game of guessing who said the quotes~~
- Make a cache, open file globally, save it, don't close it
- Embed colors for bot messages (refer below for resources)
- Add feature to quote multiple lines from one user
- Add feature to associate quote snippets with others users included in message snippet
- Add attachment quoting support (ability to quote screenshots, sound files or picture attachments)
- Add "nice navigation" (page flipping for listing quotes)


## Note to contributers
- ~~Do not use client.run(), use bot.run() instead as "bot" is a subclass of "client. bot.run() can do everything client can do and more.~~

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