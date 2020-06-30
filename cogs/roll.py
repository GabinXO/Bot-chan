import discord
from discord.ext import commands
from database import *
from config import *
import random
from descriptions import ROLL_BRF, ROLL_DSC


class Roll(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['r'], brief=ROLL_BRF, description=ROLL_DSC)
    async def roll(self, ctx):
        user = ctx.author
        check_user_exists(user)
        wait = check_last_roll(user)
        if wait <= 0:
            rarity = pick_random_rarity()
            chan_id, chan_name, chan_rarity = pick_random_chan(rarity)
            add_to_inventory(user, chan_id)
            rarity_name = RARITIES[chan_rarity][0].upper()
            print(f'{user.name} rolled {rarity_name} {chan_name}')
            embed = discord.Embed()
            embed.title = rarity_name
            embed.colour = RARITIES[chan_rarity][1]
            embed.description = f'{chan_name}'
            file = get_image(chan_name)
            embed.set_image(url="attachment://image.png")
            await ctx.send(file=file, embed=embed)
            if check_level(user, chan_id):
                await ctx.send(f'**Your {chan_name} leveled up!**')
            update_inventory_price(user)
            while check_rank(user):  # While in case he rank up multiple times
                user_rank = get_rank(user)
                rank_name = RANKS[user_rank][0]
                stars = get_prestige_stars(user)
                await ctx.send(f'**You have been promoted to {rank_name}{stars}!**')
        else:
            wait_str = seconds_converter(wait)
            await ctx.send(f'You have to wait for {wait_str}.')


def pick_random_rarity():
    '''Uses the rates form config.py, returns an integrer.'''
    return random.choices([0, 1, 2, 3, 4], RATES)[0]


def pick_random_chan(rarity):
    '''Pick a random chan from the selected rarity.
    Returns her id, her name and her rarity.'''
    query = f'SELECT id, name, rarity FROM chans WHERE rarity={rarity};'
    chan_list = mysql_get(query)
    chan = random.choice(chan_list)
    return chan


def add_to_inventory(user, chan_id):
    table_name = 'u' + str(user.id)
    query = f'SELECT chan_level FROM {table_name} WHERE chan_id={chan_id};'
    if mysql_get(query) == []:  # If the user doesn't already have one
        query = f'''INSERT INTO {table_name}(chan_id, chan_level, chan_progress)
                    VALUES({chan_id}, 1, 1);'''
        mysql_set(query)
    else:
        query = f'SELECT chan_progress FROM {table_name} WHERE chan_id={chan_id};'
        chan_progress = mysql_get(query)[0][0]
        query = f'''UPDATE {table_name}
                    SET chan_progress={chan_progress+1} WHERE chan_id={chan_id};'''
        mysql_set(query)


def level_up(table_name, chan_id, chan_level):
    '''Level a chan up and set her progress to 0.'''
    query = f'''UPDATE {table_name} SET chan_level={chan_level+1},
                chan_progress=0 WHERE chan_id={chan_id}'''
    mysql_set(query)


def check_level(user, chan_id):
    '''Returns if the chan can level up. Level her up if she can.'''
    table_name = 'u' + str(user.id)
    query = f'''SELECT chan_level, chan_progress FROM {table_name}
                WHERE chan_id={chan_id};'''
    chan_level, chan_progress = mysql_get(query)[0]
    chan_needed = 2**chan_level
    if chan_progress == chan_needed:
        level_up(table_name, chan_id, chan_level)
        return True
    else:
        return False


def rank_up(user, user_rank):
    '''Rank a user up.'''
    query = f'''UPDATE users SET user_rank={user_rank+1}
                WHERE id={user.id}'''
    mysql_set(query)


def check_rank(user):
    '''Returns if the user can rank up. Rank him up if he can.'''
    query = f'''SELECT inventory_price, user_rank FROM users
                WHERE id={user.id};'''
    inventory_price, user_rank = mysql_get(query)[0]
    if user_rank < len(RANKS) - 1:  # Can't rank up if he's at the max level
        next_rank = RANKS[user_rank + 1][1]
        if inventory_price >= next_rank:
            rank_up(user, user_rank)
            return True
        else:
            return False
    else:
        return False


def seconds_converter(seconds):
    '''Converts seconds to a time string.'''
    minutes = seconds // 60
    seconds %= 60
    hours = minutes // 60
    minutes %= 60
    seconds = str(seconds)
    minutes = str(minutes)
    hours = str(hours)
    if int(hours) > 0:
        if len(seconds) <= 1:
            seconds = '0' + seconds
        if len(minutes) <= 1:
            minutes = '0' + minutes
        line = f'{hours}h {minutes}m {seconds}s'
    elif int(minutes) > 0:
        if len(seconds) <= 1:
            seconds = '0' + seconds
        line = f'{minutes}m {seconds}s'
    else:
        line = f'{seconds}s'
    return line


def setup(client):
    client.add_cog(Roll(client))
