import discord
from discord.ext import commands
from database import *
from config import *
import random


class Roll(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['r'], brief='Roll a random chan')
    async def roll(self, ctx):
        user = ctx.author
        check_user_exists(user)
        wait = check_last_roll(user)
        if wait <= 0:
            rarity = pick_random_rarity()
            chan_id, chan_name, chan_rarity = pick_random_chan(rarity)
            add_to_inventory(user, chan_id)
            print(f'{user.name} rolled {chan_name} ({RARITY[chan_rarity][0]})')
            embed = discord.Embed()
            embed.title = RARITY[chan_rarity][0]
            embed.colour = RARITY[chan_rarity][1]
            embed.description = f'*{chan_name}*'
            file = get_image(chan_name)
            embed.set_image(url="attachment://image.png")
            await ctx.send(file=file, embed=embed)
            if check_level(user, chan_id):
                await ctx.send(f'**Your {chan_name} leveled up!**')
            update_inventory_price(user)
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

def seconds_converter(seconds):
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
