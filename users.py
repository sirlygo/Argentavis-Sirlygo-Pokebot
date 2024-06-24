from db import USERS
import embeds

"""
This module handles user profiles and the onboarding system.
"""

async def profile(message):
    """Show a profile, making a new user if needed."""
    new = False
    if message.author.id not in USERS:
        new_user(message.author)
        new = True
    tosay = "Welcome to the community!" if new else ""
    await message.reply(tosay, embed = embeds.profile(message.author))


def new_user(user):
    # Possibly using a class in addition to this 
    # might help with if i ever must change the user struct?
    u = {}
    u["uid"] = user.id

    u["bp"] = 0

    u["items"] = {"pokeball": 5}

    u["pokemon"] = []


    u["battles"] = []

    USERS[user.id] = u
    