from enum import Enum
from typing import Optional
from dataclasses import dataclass, field

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