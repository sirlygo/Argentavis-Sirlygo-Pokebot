from frequency_cache import Frequency_Cache

"""
This module stores references to cache objects so other modules can access them.
"""

USERS = Frequency_Cache(100, "data/users/", static=False)
ITEMS = Frequency_Cache(100, "data/items/")



def save_db():
    print("Saving databases...")
    dexes = [USERS]
    for dex in dexes:
        dex.save_items() # Static dexes will ignore this.