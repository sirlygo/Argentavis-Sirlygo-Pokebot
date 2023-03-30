from enum import Enum

"""
,pokedex_number,name,,,generation,status,species,
type_number,type_1,type_2,height_m,weight_kg,
abilities_number,ability_1,ability_2,ability_hidden,
total_points,hp,attack,defense,sp_attack,sp_defense,speed,
catch_rate,base_friendship,base_experience,growth_rate,
,,,,,
,,,,,,
,,,,,,
,,,,,

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
    type_2 : Elemental_Type
    
    height_m : float
    weight_kg : float
    
    ability_1 : str
    ability_2 : str
    ability_hidden : str
    
    bst : int
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
    
    
    @classmethod
    def from_file(cls, file_path):
        "Create a pokemon from a csv."
        return Person('John', 'Doe', 25)