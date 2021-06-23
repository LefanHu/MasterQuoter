from discord.ext import commands
import os
import requests
from bs4 import BeautifulSoup
from anytree import Node, RenderTree


class Tree(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["pr"], hidden=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def parent(self, ctx, item):

        URL = "https://calamitymod.fandom.com/wiki/" + str(item)
        page = requests.get(URL)
        lst = []

        soup = BeautifulSoup(page.content, "html.parser")
        crafts = soup.find("td", class_="ingredients")
        parent = soup.find("td", class_="result")

        if parent == None:
            await ctx.send("This item does not craft anything. ")
            return

        ingredients = crafts.find_all("span", class_="i")
        for ingredient in ingredients:
            lst.append(ingredient)

        top = Node(parent.text, parent=None)
        for i in range(len(lst)):
            Node(lst[i].text, parent=top)

        out = "\n"
        for pre, fill, node in RenderTree(top):
            out += "%s%s\n" % (pre, node.name)

        await ctx.send("```" + out + "```")

    @commands.command(aliases=["ing"], hidden=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def ingredients(self, ctx, inp):

        inp = '_'.join(word.capitalize() for word in inp.split(' '))
        URL = 'https://calamitymod.fandom.com/wiki/' + inp
        page = requests.get(URL)
        vals = []

        soup = BeautifulSoup(page.content, "html.parser")

        crafts = soup.find(id="global-wrapper")

        ingredients = crafts.find_all('span', class_='i break block alignleft')

        for item in ingredients:
            vals.append(item)

        top = Node(inp, parent = None)
        for i in range(len(vals)):
            Node(vals[i].text, parent=top)

        out = "\n"
        for pre, fill, node in RenderTree(top):
            out += "%s%s\n" % (pre, node.name)
        await ctx.send('```' + out+ "```")



    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up(os.path.basename(__file__)[:-3])


def setup(bot):
    bot.add_cog(Tree(bot))
