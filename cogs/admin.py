import discord
from discord.ext import commands
from config import ADMINS_IDS


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(brief='Kill the bot process')
    async def kill(self, ctx):
        if ctx.author.id in ADMINS_IDS:
            print('Bot-chan is offline!')
            await self.client.close()
        else:
            await ctx.send(':no_entry: You don\'t have access to this command.')


def setup(client):
    client.add_cog(Admin(client))
