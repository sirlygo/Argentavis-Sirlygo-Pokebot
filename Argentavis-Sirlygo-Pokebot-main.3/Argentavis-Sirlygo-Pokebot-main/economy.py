import discobot_modules.text_coloring as tc
from db import USERS
from db import ITEMS
import embeds

"""
This module handles inventory and shop system.
"""


async def send_shop_screen(message):
    em = embeds.shop()
    await message.reply(embed = em)

async def buy(message, item_key):
    uid = message.author.id
    if uid not in USERS:
        print(f"{tc.R}Cannot grant item {tc.W}\"{item_key}\"{tc.R} to user because there is no user with this uid:\n{tc.B}{uid}{tc.W}")
        return
    if item_key not in ITEMS:
        print(f"{tc.R}Cannot grant item {tc.W}\"{item_key}\"{tc.R} No item exists.{tc.W}")
        return
    item = ITEMS[item_key]
    user = USERS[uid]
    item_name = item["name"]
    if user["bp"] < item["price"]:
        await message.reply(f"You're too poor to afford a {item_name}. Come back when you're a little... *mmmm...* Richer.")
        return
    # Perform Transaction
    user_gain_item(uid, item_key)
    user["bp"] -=item["price"]
    USERS[uid] = user
    await message.reply(f"Here's your {item_name}! We hope to see you again!")



def user_item_count(uid, item_key):
    if item_key not in USERS[uid]["items"]:
        return 0
    return USERS[uid]["items"][item_key]

def user_gain_item(uid, item_key, qty=1):
    """
    Grant an item to a user and save to db.

    Fail and print to the console if the user is invalid,
    or if negative items are passed.
    """
    if uid not in USERS:
        print(f"{tc.R}Cannot grant item {tc.W}\"{item_key}\"{tc.R} to user because there is no user with this uid:\n{tc.B}{uid}{tc.W}")
        return
    if qty < 0:
        print(f"{tc.O}Warning: tried to give {qty} {tc.W}\"{item_key}\"{tc.O} to user {tc.B}{uid}{tc.O}\nQuantity converted to positive.{tc.W}")
        qty = -qty
    user = USERS[uid]
    if item_key not in user["items"]:
        user["items"][item_key] = qty
    else:
        user["items"][item_key] += qty

    USERS[uid] = user

def user_spend_item(uid, item_key, qty=1):
    """
    Take an item from a user and save to db

    Fail and print to the console if the user is invalid,
    or if negative items are passed.

    Return a bool that represents if the user succsesfully spent or didnt have enought.
    """
    if uid not in USERS:
        print(f"{tc.R}Cannot grant item {tc.W}\"{item_key}\"{tc.R} to user because there is no user with this uid:\n{tc.B}{uid}{tc.W}")
        return
    if qty < 0:
        print(f"{tc.O}Warning: tried to give {qty} {tc.W}\"{item_key}\"{tc.O} to user {tc.B}{uid}{tc.O}\nQuantity converted to positive.{tc.W}")
        qty = -qty
    user = USERS[uid]
    if item_key not in user["items"]:
        return False
    if user["items"][item_key] < qty:
        return False
    user["items"][item_key] -= qty
    USERS[uid] = user
    return True