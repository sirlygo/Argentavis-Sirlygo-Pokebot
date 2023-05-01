from collections import OrderedDict
import json
import os

class Frequency_Cache:
    """
    Represents a caching system to retrieve json files from a directory.
    It stores a certain number of objects before evicting the least
    frequently accessed item from the cache.

    Can specify a unique path and max size.
    Can specify static or non-static.
    non-static caches will save their data 
    to its file before decaching it.
    """
    def __init__(self, max_size, path_prefix, decay_factor=0.9, static=True):
        self.max_size = max_size           # Maximum number of items in the cache
        self.path_prefix = path_prefix     # Prefix for database path
        self.static = static               # Determines if the database is mutable
        self.cache = OrderedDict()         # Ordered dictionary to store cache items
        self.access_count = {}             # Dictionary to store access counts for each item
        self.decay_factor = decay_factor   # Factor to decay access counts

    def __contains__(self, key):
        if key in self.cache:
            # Happy Path, it's easily true
            return True
        else:
            path = f"{self.path_prefix}{key}.json"
            return os.path.isfile(path)



    def __getitem__(self, key):
        if key in self.cache:
            # Happy Path, move this item to the end so it's sorted by recency
            self.cache.move_to_end(key)
        else:
            # If the item is not in the cache, load it from the JSON file
            with open(f"{self.path_prefix}{key}.json", "r+", encoding="utf-8") as f:
                print(f"{self.path_prefix}{key}.json")
                data = json.load(f)
            # Call __setitem__ to add new value and decache old ones
            self[key] = data

        # Both Paths converge here.
        # Decay all access counts and increment this one.
        for k in self.access_count.keys():
            self.access_count[k] *= self.decay_factor
        self.access_count[key] += 1

        return self.cache[key]

    def __setitem__(self, key, newvalue):
        # Add the item and initialize the access count to 0. 
        # If it is being accessed by __getitem__, increment later.
        self.cache[key] = newvalue
        if key not in self.access_count: # if there's already a value in access_count, keep it
            self.access_count[key] = 0
        if len(self.cache) > self.max_size:
            # If full, remove least accessed item from cache.
            # ChatGPT:
            # "In this version, the min() function uses a lambda function 
            # as the key argument that sorts items first by access count 
            # and then by insertion order."
            least_accessed = min(self.cache, key=lambda k: (self.access_count[k], self.cache[k]))
            if not self.static:
                self.save_item(least_accessed)
            self.cache.pop(least_accessed)
            #self.access_count.pop(least_accessed) # Keep track of accesses even after data is freed.
            # I'm ok storing 1000 integers in RAM.

    def save_item(self, key):
        if self.static:
            return
        with open(f"{self.path_prefix}{key}.json", "w+", encoding="utf-8") as file: 
            json.dump(self.cache[key], file)

    def save_items(self):
        if self.static:
            return
        for key in self.cache:
            self.save_item(key)
            