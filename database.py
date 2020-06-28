import mysql.connector
from discord import File
from passwords import *
from config import *
from time import time


def mysql_get(query):
    cnx = mysql.connector.connect(
        user=USER,
        password=PWD,
        host=HOST,
        database=DB,
    )
    cursor = cnx.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    cnx.close()
    return rows


def mysql_set(query):
    cnx = mysql.connector.connect(
        user=USER,
        password=PWD,
        host=HOST,
        database=DB,
    )
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit()
    cursor.close()
    cnx.close()


def get_image(chan_name):
    '''Returns a discord file object.'''
    image_name = chan_name.lower()
    for sub in (' ', '-'):
        image_name = image_name.replace(sub, '_')
    path = f'images/{image_name}.jpg'
    file = File(path, filename='image.png')
    return file


def add_user(user):
    query = f'''INSERT INTO users(id, last_roll, roll_count, inventory_price, username)
                VALUES({user.id},0,0,0,\'{user.name}\');'''
    mysql_set(query)
    table_name = 'u' + str(user.id)
    query = f'''CREATE TABLE {table_name} (
	           chan_id MEDIUMINT PRIMARY KEY,
               chan_level TINYINT,
               chan_progress SMALLINT
               );'''
    mysql_set(query)

def update_username(user):
    query = f'SELECT username FROM users WHERE id = {user.id};'
    username = mysql_get(query)
    if user.name != username:
        query = f'UPDATE users SET username = \'{user.name}\' WHERE id = {user.id};'


def check_user_exists(user):
    '''Checks if the user exists, add it to the database if not.'''
    query = f'SELECT last_roll FROM users WHERE id={user.id};'
    answer = mysql_get(query)
    if answer == []:
        add_user(user)
    update_username(user)


def reset_account(user):
    query = f'DELETE FROM users WHERE id={user.id};'
    mysql_set(query)
    query = f'DROP TABLE u{user.id};'
    mysql_set(query)


def add_roll(user):
    '''Add 1 roll to the user stats.'''
    query = f'SELECT roll_count FROM users WHERE id={user.id};'
    roll_count = mysql_get(query)[0][0] + 1
    query = f'UPDATE users SET roll_count={roll_count} WHERE id={user.id};'
    mysql_set(query)


def get_last_roll(user):
    query = f'SELECT last_roll FROM users WHERE id={user.id};'
    last_roll = mysql_get(query)[0][0]
    return last_roll


def check_last_roll(user):
    '''Returns the time to wait for the next roll.
    Update his last roll if he can roll.'''
    last_roll = get_last_roll(user)
    actual_time = time()
    wait = round(ROLL_INTERVAL - (actual_time - last_roll))
    if wait > 0:
        return wait
    else:
        query = f'UPDATE users SET last_roll={actual_time} WHERE id={user.id};'
        mysql_set(query)
        add_roll(user)
        return 0  # Used to not return big negative values


def get_chan_count(user, rarity=-1):
    '''rarity : int, used to specify a rarity, by default all.'''
    table_name = 'u' + str(user.id)
    if rarity < 0:
        query = f'SELECT COUNT(*) FROM {table_name};'
    else:
        query = f'''SELECT COUNT(*) FROM {table_name} LEFT JOIN chans
                    ON {table_name}.chan_id = chans.id
                    WHERE chans.rarity = {rarity};'''
    count = mysql_get(query)[0][0]
    return count


def get_chan_total_count(rarity=-1):
    '''rarity : int, used to specify a rarity, by default all.'''
    if rarity < 0:
        query = 'SELECT COUNT(*) FROM chans;'
    else:
        query = f'SELECT COUNT(*) FROM chans WHERE rarity={rarity};'
    count = mysql_get(query)[0][0]
    return count


def calculate_inventory_price(user, rarity=-1):
    '''rarity : int, used to specify a rarity, by default all.'''
    table_name = 'u' + str(user.id)
    inventory_price = 0
    if rarity < 0:
        query = f'''SELECT {table_name}.chan_level, chans.rarity
                    FROM {table_name} LEFT JOIN chans
                    ON {table_name}.chan_id = chans.id;'''
        chan_list = mysql_get(query)
    else:
        query = f'''SELECT {table_name}.chan_level, chans.rarity
                    FROM {table_name} LEFT JOIN chans
                    ON {table_name}.chan_id = chans.id
                    WHERE chans.rarity = {rarity}'''
        chan_list = mysql_get(query)
    for chan in chan_list:
        chan_level, chan_rarity = chan
        chan_value = RARITY[chan_rarity][2]
        inventory_price += chan_value * (2 ** (chan_level - 1))
    return inventory_price


def update_inventory_price(user):
    inventory_price = calculate_inventory_price(user)
    query = f'UPDATE users SET inventory_price={inventory_price} WHERE id={user.id}'
    mysql_set(query)


def get_inventory_price(user_id):
    query = f'SELECT inventory_price FROM users WHERE id={user_id}'
    inventory_price = mysql_get(query)[0][0]
    return inventory_price
