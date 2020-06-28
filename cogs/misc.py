import discord
from discord.ext import commands


class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        activity = discord.Game(name = 'Start by typing \'help')
        await self.client.change_presence(activity = activity)
        print('Bot-chan is online!')

    @commands.command(brief='Shows the bot\'s ping')
    async def ping(self, ctx):
        await ctx.send(f'{round(self.client.latency*1000)} ms')


def setup(client):
    client.add_cog(Misc(client))
