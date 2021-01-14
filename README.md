# Description
Master Quoter is a quote bot made by team "MasterBaiters" designed to save and snip all the best quotes made by your friends. A great addition to any lively discord server.

Work-in-progress :) (by 2 idiots in high school)

## Current TODO list
- If quotes of one user exceed a total of 2000 characters, command !qlist @user will crash due to discord message limit
- Save multiple quotes at the same time (avoids unneccessary file openings and closings)
- Add time and date information to quotes
- Add server id to quotes
- Change structure in how quotes are saved
- Add environment variables for bot token
- Add error handling "bot.event"
- Fix first time quote initialization. If quotes.json is empty but still exists, bot will not work.

## Future plans
- ~~Implement listing quotes for specific people~~
- ~~Implement game of guessing who said the quotes~~
- Make a cache, open file globally, save it, don't close it
- Embed colors for bot messages (refer below for resources)
- Add feature to quote multiple lines from one user
- Add feature to associate quote snippets with others users included in message snippet
- Add attachment quoting support (ability to quote screenshots or picture attachments)


## Note to contributers
Do not use client.run(), ruse bot.run() instead as "bot" is a subclass of "client.

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
