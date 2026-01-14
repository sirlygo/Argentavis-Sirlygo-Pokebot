from enum import Enum
from typing import Optional
from dataclasses import dataclass, field
import random



"""
This module defines classes for specieses and individuals.

These classes have data on how these objects behave, as well as how to load them from file or save them.

In this project, each species is a species (or form?) of pokemon,
and each individual is an individual pokemon in the wild or in your collection.

The csv dataset i used is below.

https://www.kaggle.com/datasets/mariotormo/complete-pokemon-dataset-updated-090420?resource=download&select=pokedex_%28Update_05.20%29.csv

thanks mario
"""


type_names = [
    "normal",
    "grass",
    "water",
    "fire",
    "electric",
    "bug",
    "poison",
    "flying",
    "rock",
    "ground",
    "ghost",
    "psychic",
    "fighting",
    "ice",
    "dragon",
    "dark",
    "steel",
    "fairy",
    "???"
    ]

Elemental_Type = Enum("Elemental_Type", type_names)

@dataclass
class Species():

    pokedex_number : int
    name : str
    generation : int
    status : str
    pokedex_species : str

    type_1 : Elemental_Type
    type_2 : Optional[Elemental_Type]

    height_m : float
    weight_kg : float

    ability_1 : str
    ability_2 : str
    ability_hidden : str

    hp : int
    attack : int
    defense : int
    sp_attack : int
    sp_defense : int
    speed : int

    catch_rate : int
    base_friendship : int # i'm not sure what this value does?
    base_experience : int # i'm not sure what this value does?
    growth_rate : str


    def get_bst(self):
        return self.hp + self.attack + self.defense + self.sp_attack + self.sp_defense + self.speed

    def get_stats_list(self):
        """Format stats as a list with 6 elements."""
        return [
            self.hp,
            self.attack,
            self.defense,
            self.sp_attack,
            self.sp_defense,
            self.speed
        ]
    def get_elemental_typing(self):
        """Put typing into a list with one or two elements."""
        elemental_typing = [self.type_1]
        if self.type_2:
            elemental_typing.append(self.type_2)
        return elemental_typing

    def get_abilities(self):
        """Put abilities in a list."""
        abilities = [self.ability_1]
        if self.ability_2:
            abilities.append(self.ability_2)
        if self.ability_hidden:
            abilities.append(self.ability_hidden)
        return abilities

    def naive_image(self, shiny = False):
        """Access pokemondb for shiny/normal sprites."""
        shiny = "shiny" if shiny else "normal"
        return f"https://img.pokemondb.net/sprites/home/{shiny}/2x/{self.name.lower()}.jpg"


    def naive_icon(self, shiny = False):
        """Access pokemondb for icons."""
        return f"https://img.pokemondb.net/sprites/sword-shield/icon/{self.name.lower()}.png"

    @classmethod
    def from_data(cls, d):
        """
        Take a list of string values and convert them to the right structure.

        The CSV file used for this project has relevent data in this structure:

        ,pokedex_number,name,,,generation,status,species,
        ,type_1,type_2,height_m,weight_kg,
        ,ability_1,ability_2,ability_hidden,
        ,hp,attack,defense,sp_attack,sp_defense,speed,
        catch_rate,base_friendship,base_experience,growth_rate,
        ,,,,,
        ,,,,,,
        ,,,,,,
        ,,,,,
        """

        # Use int(float()) pattern to convert "18.0" into 18.
        return cls(
        pokedex_number  = int(float(d[1])),
        name            = d[2],
        generation      = int(float(d[5])),
        status          = d[6],
        pokedex_species = d[7],

        type_1          = Elemental_Type[d[9].lower()],
        type_2          = Elemental_Type[d[10].lower()] if d[10] else None,

        height_m        = d[11],
        weight_kg       = d[12],

        ability_1       = d[14],
        ability_2       = d[15],
        ability_hidden  = d[16],

        hp              = int(float(d[18])),
        attack          = int(float(d[19])),
        defense         = int(float(d[20])),
        sp_attack       = int(float(d[21])),
        sp_defense      = int(float(d[22])),
        speed           = int(float(d[23])),

        catch_rate      = int(float(d[24])) if d[24] else 1,
        base_friendship = d[25],
        base_experience = d[26],
        growth_rate     = d[27]
        )

    @classmethod
    def load_index(cls, pokedex_number, file_path = "data/pokedex.csv"):
        """
        Load a species from a csv file.

        This is done by simply looping through the list until we find the right natdexno.
        """
        with open(file_path, "r+", encoding="utf-8") as f:

            for dexentry in f.read().splitlines():
                d = dexentry.split(",")

                if str(pokedex_number) == d[1]:
                    # Use int(float()) pattern to convert "18.0" into 18.
                    return Species.from_data(d)


@dataclass
class Held_item():
    name : str


class Individual():
    """
    This represents an individual in your collection.
    """
    def __init__(self, species, nickname = None, level= 1, shiny=None):
        self.species = species
        self.nickname = nickname
        self.level = level
        self.shiny = shiny if shiny is not None else random.randint(1,8192) == 8192
        #self.evs : Evs
        #self.ivs : Ivs
        #self.held_item : Optional[Held_Item] = None

    def get_name(self):
        """
        An individual's name might be a nickname or it's species name.
        """
        if not self.nickname:
            return self.species.name
        return self.nickname
    def get_title(self):
        """
        An individual's name might be a nickname or it's species name.
        Disambiguate what part is the name and what is the species.
        """
        if not self.nickname:
            return self.species.name
        if self.nickname == self.species.name:
            return self.species.name
        return f"{self.nickname} ({self.species.name})"

    def get_stats(self):
        """
        WIP calculation of an individuals's stats as it levels up.
        """
        return {
        "hp" : self.species.hp * self.level / 100,
        "attack" : self.species.attack * self.level / 100,
        "defense" : self.species.defense * self.level / 100,
        "sp_attack" : self.species.sp_attack * self.level / 100,
        "sp_defense" : self.species.sp_defense * self.level / 100,
        "speed" : self.species.speed * self.level / 100
        }

    def get_stats_list(self):
        """Format stats as a list with six elements instead of a dict."""
        stats = self.get_stats()
        return [
            stats["hp"],
            stats["attack"],
            stats["defense"],
            stats["sp_attack"],
            stats["sp_defense"],
            stats["speed"]
        ]

    @classmethod
    def from_dict(cls, data):
        """Load an individual from a dict, like how it might be stored in file."""
        req_keys = [
        "nickname",
        "species",
        "level",
        "shiny",
        "item",
        "ivs",
        "evs"
        ]
        if not all(key in data for key in req_keys):
            # If something is missing, we can't make a pokemon.
            return None

        nickname = data["nickname"]
        species = Species.load_index(data["species"])
        level = data["level"]
        shiny = data["shiny"]
        #self.item = Item(data["item"]) if data["item"] else None
        #self.ivs = data["ivs"]
        #self.evs = data["evs"]
        return cls(species, nickname, level, shiny)

    def to_dict(self):
        data = dict()
        data["nickname"] = self.nickname
        data["species"] = self.species.pokedex_number
        data["level"] = self.level
        data["shiny"] = self.shiny
        data["item"] = ""#self.item.name if self.item else ""
        data["ivs"] = ""# self.ivs
        data["evs"] = ""# self.evs
        return data

# Precalculated value, sum of all catch weights of all pokemon.
TOTAL_CATCH_RATE = 79195

def random_encounter():
    """"
    Select a random pokemon. 
    Pokemon with an easier catch rate are more common.
    """
    progress = random.randint(0,TOTAL_CATCH_RATE)
    with open("data/pokedex.csv", "r+", encoding="utf-8") as f:
        for dexentry in f.read().splitlines():
            d = dexentry.split(",")
            #skip the first csv
            if d[1] == "pokedex_number":
                continue
            cr = int(float(d[24])) if d[24] else 1
            progress -= cr
            if progress <= 0:
                spec = Species.from_data(d)
                return Individual(spec)


if __name__ == "__main__":
    print(Species.load_index(25)  )
    print()
    print(Species.load_index(151) )
    print()
    print(Species.load_index(251) )
    print()
    print(Species.load_index(386) )
    print()
    print(Species.load_index(493) )
    print()
    print(Species.load_index(649) )

    print(random_encounter())
    print(random_encounter())
    print(random_encounter())
    print(random_encounter())
    print(random_encounter())


def calc_all_cr():
    """Pre-calculate the total catch rate in the pokemon csv."""
    print("Calcing catch rates...")
    total_cr = 0
    for i in range(890):
        try:
            mon = Species.load_index(i+1)
            total_cr += mon.catch_rate
        except Exception:
            print(f"Failed on thing {i+1}")
            raise exception
    print("Calc done!")
    print(total_cr)