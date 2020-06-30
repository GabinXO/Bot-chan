import discord
from discord.ext import commands
from database import *
from config import RANKS
from descriptions import RANKS_BRF, RANKS_DSC, PREST_BRF, PREST_DSC


class Ranks(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['rank'], brief=RANKS_BRF, description=RANKS_DSC)
    async def ranks(self, ctx):
        user = ctx.author
        check_user_exists(user)
        msg = []
        user_rank = get_rank(user)
        for i in range(len(RANKS)):
            if i == user_rank:  # Emphazises your rank
                rank_name = f'**[{RANKS[i][0].upper()}]**'
            else:
                rank_name = f'[{RANKS[i][0].upper()}]'
            rank_pts = RANKS[i][1]
            line = f'{rank_name} : {rank_pts} pts'
            msg.append(line)
        msg.append('')
        if user_rank < len(RANKS) - 1:
            stars = get_prestige_stars(user)
            next_rank_name = f'[{RANKS[user_rank+1][0].upper()}{stars}]'
            inventory_price = get_inventory_price(user.id)
            next_rank_needed = RANKS[user_rank + 1][1] - inventory_price
            msg.append(f'{next_rank_needed} pts before {next_rank_name}!')
        else:
            msg.append('You\'re at the highest rank!')
            msg.append('Try \'prestige!')
        embed = discord.Embed()
        embed.colour = 0xe74c3c
        embed.title = 'Ranks'
        embed.description = '\n'.join(msg)
        await ctx.send(embed=embed)

    @commands.command(aliases=['prestige'], brief=PREST_BRF, description=PREST_DSC)
    async def prest(self, ctx):
        user = ctx.author
        check_user_exists(user)
        user_id = user.id
        username = user.display_name
        user_rank = get_rank(user)
        if user_rank < len(RANKS) - 1:
            text = 'You need to be at the highest rank.'
            message = await ctx.send(text)
        else:
            text = '**This action delete ALL your chans.'
            text += 'Are you sure you want to prestige? (Y/N)**'
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
                    prestige(user)
                    print(f'{user.name} prestiged')
                    await ctx.send(f'{username}\'s prestiged!')
                elif reaction.emoji == '\N{REGIONAL INDICATOR SYMBOL LETTER N}':
                    await ctx.send(f'Prestige cancelled.')
            except:
                await ctx.send('Timeout.')


def reset_inventory(user):
    query = f'''UPDATE users SET last_roll=0, inventory_price=0, user_rank=0
                WHERE id={user.id};'''
    mysql_set(query)
    query = f'TRUNCATE TABLE u{user.id};'
    mysql_set(query)


def prestige(user):
    reset_inventory(user)
    query = f'SELECT prestige FROM users WHERE id={user.id};'
    prestige = mysql_get(query)[0][0]
    query = f'UPDATE users SET prestige={prestige+1} WHERE id={user.id};'
    mysql_set(query)


def setup(client):
    client.add_cog(Ranks(client))
