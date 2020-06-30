import discord
from discord.ext import commands
from database import *
from config import RARITIES
from descriptions import INV_BRF, INV_DSC, RESET_BRF, RESET_DSC


class Inventory(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['i', 'inventory'], brief=INV_BRF, description=INV_DSC)
    async def inv(self, ctx):
        user = ctx.author
        check_user_exists(user)
        username = user.display_name
        chan_count = get_chan_count(user)
        inventory_price = get_inventory_price(user.id)
        embed = discord.Embed()
        embed.title = f'{username}\'s Inventory'
        embed.colour = 0xe74c3c
        embed.description = f'**{chan_count} chans | {inventory_price} pts**'
        for rarity in range(5):
            chan_list = get_chan_list(user, rarity)
            if chan_list != []:  # Prevent an error if there's no chans
                embed.add_field(name=get_field_name(user, rarity),
                                value='\n'.join(chan_list), inline=False)
        await ctx.send(embed=embed)

    @commands.command(brief=RESET_BRF, description=RESET_DSC)
    async def reset(self, ctx):
        user = ctx.author
        check_user_exists(user)
        user_id = user.id
        username = user.display_name
        text = '**Are you sure you want to reset your account FOREVER? (Y/N)**'
        message = await ctx.send(text)
        await message.add_reaction('\N{REGIONAL INDICATOR SYMBOL LETTER Y}')
        await message.add_reaction('\N{REGIONAL INDICATOR SYMBOL LETTER N}')

        def check(reaction, user):
            return user.id == user_id and reaction.message.id == message.id and reaction.emoji in [
                '\N{REGIONAL INDICATOR SYMBOL LETTER Y}',
                '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
            ]

        try:
            reaction, user = await self.client.wait_for('reaction_add',
                                                        check=check,
                                                        timeout=20.0)
            if reaction.emoji == '\N{REGIONAL INDICATOR SYMBOL LETTER Y}':
                reset_account(user)
                print(f'{user.name}\'s account has been reset')
                await ctx.send(f'{username}\'s account has been reset.')
            elif reaction.emoji == '\N{REGIONAL INDICATOR SYMBOL LETTER N}':
                await ctx.send(f'{username}\'s account has not been reset.')
        except:
            await ctx.send('Timeout.')


def get_chan_list(user, rarity):
    # Get the data from the database
    table_name = 'u' + str(user.id)
    query = f'''SELECT chans.name, {table_name}.chan_level,
                {table_name}.chan_progress FROM {table_name}
                LEFT JOIN chans ON {table_name}.chan_id = chans.id
                WHERE chans.rarity = {rarity}
                ORDER BY {table_name}.chan_level DESC,
                {table_name}.chan_progress DESC, chans.name ASC;'''
    raw_list = mysql_get(query)
    # Turns the raw data to a pretty list
    chan_list = []
    for chan in raw_list:
        name, level, progress = chan
        next_level = 2**level
        line = f'{name} [Level {level}] ({progress}/{next_level})'
        chan_list.append(line)
    return chan_list


def get_field_name(user, rarity):
    rarity_name = RARITIES[rarity][0].upper()
    chan_count = get_chan_count(user, rarity)
    chan_total_count = get_chan_total_count(rarity)
    field_name = f'**{rarity_name} [{chan_count}/{chan_total_count}]**'
    return field_name


def setup(client):
    client.add_cog(Inventory(client))
