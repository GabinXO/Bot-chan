import discord
from discord.ext import commands
from descriptions import PING_BRF, PING_DSC, UWU_BRF, UWU_DSC


class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        activity = discord.Game(name='Start by typing \'help')
        await self.client.change_presence(activity=activity)
        print('Bot-chan is online!')

    @commands.command(brief=PING_BRF, description=PING_DSC)
    async def ping(self, ctx):
        await ctx.send(f'{round(self.client.latency*1000)} ms')

    @commands.command(brief=UWU_BRF, description=UWU_DSC)
    async def uwu(self, ctx):
        await ctx.send('UwU')


def setup(client):
    client.add_cog(Misc(client))
