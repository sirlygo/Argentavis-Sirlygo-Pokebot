from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import Dict, Iterable, List, Optional, Sequence
from dataclasses import dataclass, field
import random
import uuid
import math

import moves
import evolutions



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
        with open(file_path, "r", encoding="utf-8") as f:
            
            for dexentry in f.read().splitlines():
                d = dexentry.split(",")
                
                if str(pokedex_number) == d[1]:
                    # Use int(float()) pattern to convert "18.0" into 18.
                    return Species.from_data(d)


@dataclass
class Held_item():
    name : str


STAT_KEYS = ("hp", "attack", "defense", "sp_attack", "sp_defense", "speed")


def _growth_experience(level: int, rate: str) -> int:
    level = max(1, int(level))
    rate = (rate or "medium-slow").lower()
    if rate == "fast":
        return int(4 * (level ** 3) / 5)
    if rate == "medium-fast":
        return level ** 3
    if rate == "slow":
        return int(5 * (level ** 3) / 4)
    # medium-slow fallback
    return int((6/5) * (level ** 3) - 15 * (level ** 2) + 100 * level - 140)


def _experience_to_level(exp: int, rate: str) -> int:
    level = 1
    while _growth_experience(level + 1, rate) <= exp:
        level += 1
        if level >= 100:
            return 100
    return level


class Individual():
    """
    This represents an individual in your collection.
    """

    def __init__(
        self,
        species,
        nickname=None,
        level=1,
        shiny=None,
        instance_id=None,
        ivs: Optional[Dict[str, int]] = None,
        evs: Optional[Dict[str, int]] = None,
        experience: Optional[int] = None,
        moveset: Optional[Sequence[str]] = None,
    ):
        self.species = species
        self.nickname = nickname
        self.level = max(1, int(level))
        self.shiny = bool(shiny) if shiny is not None else random.randint(1, 8192) == 8192
        self.instance_id = instance_id or uuid.uuid4().hex
        self.ivs = self._normalise_ivs(ivs)
        self.evs = self._normalise_evs(evs)
        self.experience = self._normalise_experience(experience)
        self.moves = self._normalise_moves(moveset)
        #self.held_item : Optional[Held_Item] = None

    @staticmethod
    def _normalise_ivs(raw: Optional[Dict[str, int]]) -> Dict[str, int]:
        ivs: Dict[str, int] = {}
        if isinstance(raw, dict):
            for key in STAT_KEYS:
                value = raw.get(key)
                if value is None:
                    value = random.randint(0, 31)
                ivs[key] = int(max(0, min(31, int(value))))
        else:
            for key in STAT_KEYS:
                ivs[key] = random.randint(0, 31)
        return ivs

    @staticmethod
    def _normalise_evs(raw: Optional[Dict[str, int]]) -> Dict[str, int]:
        evs: Dict[str, int] = {}
        if isinstance(raw, dict):
            for key in STAT_KEYS:
                value = raw.get(key, 0)
                evs[key] = int(max(0, min(252, int(value))))
        else:
            for key in STAT_KEYS:
                evs[key] = 0
        total = sum(evs.values())
        if total > 510:
            # Scale down proportionally to respect the overall cap.
            factor = 510 / total if total else 0
            for key in STAT_KEYS:
                evs[key] = int(math.floor(evs[key] * factor))
        return evs

    def _normalise_experience(self, exp: Optional[int]) -> int:
        if isinstance(exp, int) and exp >= 0:
            target_level = _experience_to_level(exp, self.species.growth_rate)
            if target_level != self.level:
                self.level = target_level
            return exp
        return _growth_experience(self.level, self.species.growth_rate)

    def _default_move_candidates(self) -> List[str]:
        type_names: List[str] = []
        type_names.append(self.species.type_1.name)
        if self.species.type_2:
            type_names.append(self.species.type_2.name)
        candidates: List[str] = []
        for typename in type_names:
            candidates.extend(moves.TYPE_SIGNATURE_MOVES.get(typename, []))
        if not candidates:
            candidates.append("tackle")
        # guarantee at least two attacks
        if "quick_attack" not in candidates:
            candidates.append("quick_attack")
        return candidates

    def _normalise_moves(self, moveset: Optional[Sequence[str]]) -> List[str]:
        available = []
        if moveset:
            for name in moveset:
                if moves.get(name):
                    available.append(name)
        if not available:
            default = self._default_move_candidates()
            stage = min(len(default), max(1, (self.level + 9) // 10))
            available = default[: max(2, min(4, stage + 1))]
        return list(dict.fromkeys(available))[:4]

    def total_evs(self) -> int:
        return sum(self.evs.values())

    def remaining_ev_capacity(self) -> int:
        return max(0, 510 - self.total_evs())
    
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
    
    def _stat_value(self, base: int, iv: int, ev: int, is_hp: bool) -> int:
        level = self.level
        ev_term = ev // 4
        if is_hp:
            return int(math.floor(((2 * base + iv + ev_term) * level) / 100) + level + 10)
        return int(math.floor(((2 * base + iv + ev_term) * level) / 100) + 5)

    def get_stats(self):
        """Calculate the battle stats for this individual."""
        return {
            "hp": self._stat_value(self.species.hp, self.ivs["hp"], self.evs["hp"], True),
            "attack": self._stat_value(self.species.attack, self.ivs["attack"], self.evs["attack"], False),
            "defense": self._stat_value(self.species.defense, self.ivs["defense"], self.evs["defense"], False),
            "sp_attack": self._stat_value(self.species.sp_attack, self.ivs["sp_attack"], self.evs["sp_attack"], False),
            "sp_defense": self._stat_value(self.species.sp_defense, self.ivs["sp_defense"], self.evs["sp_defense"], False),
            "speed": self._stat_value(self.species.speed, self.ivs["speed"], self.evs["speed"], False),
        }

    def max_hp(self) -> int:
        return self.get_stats()["hp"]

    def get_move_names(self) -> List[str]:
        return list(self.moves)

    def get_move_objects(self) -> List[moves.Move]:
        return [moves.get(name) for name in self.moves if moves.get(name)]
    
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
        "species",
        ]
        if not data or not all(key in data for key in req_keys):
            # If something critical is missing, we can't make a pokemon.
            return None

        nickname = data.get("nickname")
        species = Species.load_index(data["species"])
        level = data.get("level", 1)
        shiny = data.get("shiny", False)
        instance_id = data.get("uid")
        raw_ivs = data.get("ivs")
        if isinstance(raw_ivs, list):
            raw_ivs = {key: raw_ivs[idx] for idx, key in enumerate(STAT_KEYS) if idx < len(raw_ivs)}
        raw_evs = data.get("evs")
        if isinstance(raw_evs, list):
            raw_evs = {key: raw_evs[idx] for idx, key in enumerate(STAT_KEYS) if idx < len(raw_evs)}
        experience = data.get("experience")
        moveset = data.get("moves")
        return cls(species, nickname, level, shiny, instance_id, raw_ivs, raw_evs, experience, moveset)

    def to_dict(self):
        data = dict()
        data["nickname"] = self.nickname
        data["species"] = self.species.pokedex_number
        data["level"] = self.level
        data["shiny"] = self.shiny
        data["uid"] = self.instance_id
        data["item"] = ""#self.item.name if self.item else ""
        data["ivs"] = {key: int(self.ivs[key]) for key in STAT_KEYS}
        data["evs"] = {key: int(self.evs[key]) for key in STAT_KEYS}
        data["experience"] = int(self.experience)
        data["moves"] = list(self.moves)
        return data

    def gain_experience(self, amount: int) -> Dict[str, List[str]]:
        amount = max(0, int(amount))
        events: Dict[str, List[str]] = {"level": [], "evolution": []}
        if amount <= 0:
            return events
        target = min(100, self.level)
        self.experience += amount
        new_level = _experience_to_level(self.experience, self.species.growth_rate)
        if new_level > self.level:
            for lvl in range(self.level + 1, new_level + 1):
                events["level"].append(f"Reached level {lvl}!")
            self.level = new_level
            # Refresh moves at certain milestones
            if len(self.moves) < 4:
                self.moves = self._normalise_moves(self.moves)
        evo = evolutions.next_evolution(self.species.pokedex_number, self.level)
        if evo:
            new_species = Species.load_index(evo)
            if new_species:
                self.species = new_species
                self.moves = self._normalise_moves(self.moves)
                events["evolution"].append(f"Evolved into {self.species.name}!")
        return events

@lru_cache(maxsize=1)
def _encounter_table(file_path="data/pokedex.csv"):
    """Load every catchable species once and cache the cumulative rates."""
    table = []
    running_total = 0
    with open(file_path, "r", encoding="utf-8") as f:
        for dexentry in f.read().splitlines():
            d = dexentry.split(",")
            if len(d) < 25 or d[1] == "pokedex_number":
                continue
            spec = Species.from_data(d)
            cr = spec.catch_rate if spec.catch_rate else 1
            running_total += cr
            table.append((running_total, spec))
    return table, running_total


def random_encounter():
    """Select a random pokemon. Easier catches appear more frequently."""
    table, total = _encounter_table()
    if not table or total <= 0:
        raise RuntimeError("Encounter table is empty; ensure pokedex data is available.")
    progress = random.randint(1, total)
    for threshold, spec in table:
        if progress <= threshold:
            return Individual(spec, level=random.randint(3, 40))
    # Fallback if rounding pushes us out of bounds.
    return Individual(table[-1][1], level=random.randint(3, 40))

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