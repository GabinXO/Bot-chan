import discord
from discord.ext import commands
from database import *
from config import RANKS
from descriptions import STATS_BRF, STATS_DSC, LEAD_BRF, LEAD_DSC


class Stats(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['s', 'statistics'], brief=STATS_BRF, description=STATS_DSC)
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
            user_rank = get_rank(user)
            rank_name = RANKS[user_rank][0]
            stars = get_prestige_stars(user)
            rank_line = f'Rank : {rank_name}{stars}'
            if user_rank < len(RANKS) - 1:
                points = get_inventory_price(user.id)
                next_rank = RANKS[user_rank + 1][1] - points
                rank_line += f' ({next_rank} pts needed)'
            desc.append(rank_line)
            roll_count = get_roll_count(user)
            desc.append(f'{roll_count} rolls')
            embed.description = '\n'.join(desc)

            collection = []
            for rarity in range(5):
                name = RARITIES[rarity][0]
                chan_count = get_chan_count(user, rarity)
                chan_total_count = get_chan_total_count(rarity)
                collection.append(f'{name} : {chan_count}/{chan_total_count}')
            chan_count = get_chan_count(user)
            chan_total_count = get_chan_total_count()
            collection.append(f'Total : {chan_count}/{chan_total_count}')
            embed.add_field(name='Collection',
                            value='\n'.join(collection), inline=False)

            prices = []
            for rarity in range(5):
                name = RARITIES[rarity][0]
                points = calculate_inventory_price(user, rarity)
                prices.append(f'{name} : {points} pts')
            inventory_price = get_inventory_price(user.id)
            prices.append(f'Total : {inventory_price} pts')
            embed.add_field(name='Points',
                            value='\n'.join(prices), inline=False)

            await ctx.send(embed=embed)

        except:
            await ctx.send('User not found.')

    @commands.command(aliases=['l', 'leaderboard'], brief=LEAD_BRF, description=LEAD_DSC)
    async def lead(self, ctx, arg=None):

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
            for row in leaderboard:
                user_id, user_points, user_name, user_rank = row
                top = get_top(user_id)
                rank = RANKS[user_rank][0].upper()
                stars = get_prestige_stars(user)
                line = f'#{top} [{rank}{stars}] {user_name} | {user_points} pts'
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
    query = f'''SELECT id, inventory_price, username, user_rank FROM users
                ORDER BY prestige DESC,
                inventory_price DESC
                LIMIT {n};'''
    leaderboard = mysql_get(query)
    return leaderboard


def setup(client):
    client.add_cog(Stats(client))
