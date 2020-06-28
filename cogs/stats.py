import discord
from discord.ext import commands
from database import *


class Stats(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['s'], brief='Shows your own or someone stats')
    async def stats(self, ctx, arg=None):

        try:
            if arg == None:
                user = ctx.author
            else:
                user = ctx.message.mentions[0]
            check_user_exists(user)
            username = user.display_name
            avatar = user.avatar_url
            embed = discord.Embed()
            embed.colour = 0xe74c3c
            embed.title = f'{username}\'s Stats'
            embed.set_thumbnail(url=avatar)

            desc = []
            top = get_top(user.id)
            desc.append(f'Top #{top}')
            points = get_inventory_price(user.id)
            desc.append(f'{points} pts')
            roll_count = get_roll_count(user)
            desc.append(f'{roll_count} rolls')
            chan_count = get_chan_count(user)
            chan_total_count = get_chan_total_count()
            desc.append(f'{chan_count}/{chan_total_count} chans')
            embed.description = '\n'.join(desc)

            prices = []
            for rarity in range(5):
                name = RARITY[rarity][0]
                points = calculate_inventory_price(user, rarity)
                line = f'{name} : {points} pts'
                prices.append(line)
            embed.add_field(name='Points By Rarities',
                            value='\n'.join(prices), inline=False)

            await ctx.send(embed=embed)

        except:
            await ctx.send('User not found.')

    @commands.command(aliases=['l', 'lead'], brief='Shows by default the top 5 players')
    async def leaderboard(self, ctx, arg=None):

        try:
            if arg == None:
                n = 5
            else:
                n = int(arg)
            user = ctx.author
            check_user_exists(user)
            leaderboard = get_leaderboard(n)
            display = []
            rank = 0
            for user in leaderboard:
                user_id, user_points, user_name = user
                rank = get_top(user_id)
                line = f'#{rank} {user_name} : {user_points} pts'
                display.append(line)
            embed = discord.Embed()
            embed.colour = 0xe74c3c
            embed.title = 'Leaderboard'
            embed.description = '\n'.join(display)
            await ctx.send(embed=embed)

        except:
            await ctx.send('Wrong argument.')


def get_top(user_id):
    inventory_price = get_inventory_price(user_id)
    query = f'''SELECT COUNT(*) FROM users
                WHERE inventory_price >= {inventory_price};'''
    top = mysql_get(query)[0][0]
    return top


def get_roll_count(user):
    query = f'SELECT roll_count FROM users WHERE id={user.id};'
    roll_count = mysql_get(query)[0][0]
    return roll_count


def get_leaderboard(n):
    '''n : int, get the n first people'''
    query = f'''SELECT id, inventory_price, username FROM users
                ORDER BY inventory_price DESC
                LIMIT {n};'''
    leaderboard = mysql_get(query)
    return leaderboard


def setup(client):
    client.add_cog(Stats(client))
