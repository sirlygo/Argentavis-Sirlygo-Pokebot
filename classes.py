from enum import Enum
from typing import Optional
from dataclasses import dataclass, field
import random

"""
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

"""
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
    base_friendship : int
    base_experience : int # ?
    growth_rate : str
    
    
    def get_bst(self):
        return self.hp + self.attack + self.defense + self.sp_attack + self.sp_defense + self.speed
    
    def get_stats_list(self):
        return [
            self.hp,
            self.attack,
            self.defense,
            self.sp_attack,
            self.sp_defense,
            self.speed
        ]
    def get_elemental_typing(self):
        elemental_typing = [self.type_1]
        if self.type_2:
            elemental_typing.append(self.type_2)
        return elemental_typing
        
    def get_abilities(self):
        abilities = [self.ability_1]
        if self.ability_2:
            abilities.append(self.ability_2)
        if self.ability_hidden:
            abilities.append(self.ability_hidden)
        return abilities
    
    @classmethod
    def from_file(cls, pokedex_number, file_path = "data/pokedex.csv"):
        """
        Load a pokemon species from a csv file.
        
        This is done by simply looping through the list until we find the right natdexno.
        """
        with open(file_path, "r+", encoding="utf-8") as f:
            
            for dexentry in f.read().splitlines():
                d = dexentry.split(",")
                
                if str(pokedex_number) == d[1]:
                    return Species(
                    pokedex_number  = d[1],
                    name            = d[2],
                    generation      = d[5],
                    status          = d[6],
                    pokedex_species = d[7],
                    
                    type_1          = Elemental_Type[d[9].lower()],
                    type_2          = Elemental_Type[d[10].lower()] if d[10] else None,
                    
                    height_m        = d[11],
                    weight_kg       = d[12],
                    
                    ability_1       = d[14],
                    ability_2       = d[15],
                    ability_hidden  = d[16],
                    
                    hp              = int(d[18]),
                    attack          = int(d[19]),
                    defense         = int(d[20]),
                    sp_attack       = int(d[21]),
                    sp_defense      = int(d[22]),
                    speed           = int(d[23]),
                    
                    catch_rate      = d[24],
                    base_friendship = d[25],
                    base_experience = d[26],
                    growth_rate     = d[27]
                    )


@dataclass
class Held_item():
    name : str


class Individual():
    """
    This represents an individual pokemon in your pokemon collection.
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
        if not self.nickname:
            return self.species.name
        return self.nickname
    def get_title(self):
        if not self.nickname:
            return self.species.name
        if self.nickname == self.species.name:
            return self.species.name
        return f"{self.nickname} ({self.species.name})"
    
    def get_stats(self):
        return {
        "hp" : self.species.hp * self.level / 100,
        "attack" : self.species.attack * self.level / 100,
        "defense" : self.species.defense * self.level / 100,
        "sp_attack" : self.species.sp_attack * self.level / 100,
        "sp_defense" : self.species.sp_defense * self.level / 100,
        "speed" : self.species.speed * self.level / 100
        }
    
    def get_stats_list(self):
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
        
        self.nickname = data["nickname"]
        self.species = Species(data["species"])
        self.level = data["level"]
        self.shiny = data["shiny"]
        #self.item = Item(data["item"]) if data["item"] else None
        #self.ivs = data["ivs"]
        #self.evs = data["evs"]
    
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

if __name__ == "__main__":
    print(Species.from_file(25)  )
    print()
    print(Species.from_file(151) )
    print()
    print(Species.from_file(251) )
    print()
    print(Species.from_file(386) )
    print()
    print(Species.from_file(493) )
    print()
    print(Species.from_file(649) )