from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class Move:
    """Represents a move a Pokémon can use in battle."""

    key: str
    name: str
    type: str
    category: str  # physical, special, or status
    power: int = 0
    accuracy: float = 1.0
    priority: int = 0
    status: Optional[str] = None
    status_chance: float = 0.0
    heal: int = 0
    description: str = ""


MOVES: Dict[str, Move] = {
    "tackle": Move("tackle", "Tackle", "normal", "physical", power=40, accuracy=0.95),
    "quick_attack": Move("quick_attack", "Quick Attack", "normal", "physical", power=40, accuracy=1.0, priority=1),
    "vine_whip": Move("vine_whip", "Vine Whip", "grass", "physical", power=45, accuracy=1.0),
    "razor_leaf": Move("razor_leaf", "Razor Leaf", "grass", "physical", power=55, accuracy=0.95),
    "sleep_powder": Move("sleep_powder", "Sleep Powder", "grass", "status", power=0, accuracy=0.75, status="sleep", status_chance=1.0),
    "ember": Move("ember", "Ember", "fire", "special", power=40, accuracy=1.0, status="burn", status_chance=0.1),
    "flame_wheel": Move("flame_wheel", "Flame Wheel", "fire", "physical", power=60, accuracy=1.0, status="burn", status_chance=0.1),
    "will_o_wisp": Move("will_o_wisp", "Will-O-Wisp", "fire", "status", power=0, accuracy=0.85, status="burn", status_chance=1.0),
    "water_gun": Move("water_gun", "Water Gun", "water", "special", power=40, accuracy=1.0),
    "bubble_beam": Move("bubble_beam", "Bubble Beam", "water", "special", power=65, accuracy=1.0),
    "aqua_tail": Move("aqua_tail", "Aqua Tail", "water", "physical", power=90, accuracy=0.9),
    "thunder_shock": Move("thunder_shock", "Thunder Shock", "electric", "special", power=40, accuracy=1.0, status="paralysis", status_chance=0.1),
    "spark": Move("spark", "Spark", "electric", "physical", power=65, accuracy=1.0, status="paralysis", status_chance=0.3),
    "thunder_wave": Move("thunder_wave", "Thunder Wave", "electric", "status", accuracy=0.9, status="paralysis", status_chance=1.0),
    "gust": Move("gust", "Gust", "flying", "special", power=40, accuracy=1.0),
    "air_slash": Move("air_slash", "Air Slash", "flying", "special", power=75, accuracy=0.95),
    "confusion": Move("confusion", "Confusion", "psychic", "special", power=50, accuracy=1.0),
    "psybeam": Move("psybeam", "Psybeam", "psychic", "special", power=65, accuracy=1.0),
    "future_sight": Move("future_sight", "Future Sight", "psychic", "special", power=120, accuracy=1.0),
    "karate_chop": Move("karate_chop", "Karate Chop", "fighting", "physical", power=50, accuracy=1.0),
    "low_sweep": Move("low_sweep", "Low Sweep", "fighting", "physical", power=65, accuracy=1.0),
    "vital_throw": Move("vital_throw", "Vital Throw", "fighting", "physical", power=70, accuracy=1.0, priority=-1),
    "scratch": Move("scratch", "Scratch", "normal", "physical", power=40, accuracy=1.0),
    "bite": Move("bite", "Bite", "dark", "physical", power=60, accuracy=1.0),
    "slam": Move("slam", "Slam", "normal", "physical", power=80, accuracy=0.75),
    "dragon_rage": Move("dragon_rage", "Dragon Rage", "dragon", "special", power=40, accuracy=1.0),
    "disarming_voice": Move("disarming_voice", "Disarming Voice", "fairy", "special", power=40, accuracy=1.0),
    "dazzling_gleam": Move("dazzling_gleam", "Dazzling Gleam", "fairy", "special", power=80, accuracy=1.0),
    "moonblast": Move("moonblast", "Moonblast", "fairy", "special", power=95, accuracy=1.0),
    "poison_sting": Move("poison_sting", "Poison Sting", "poison", "physical", power=30, accuracy=1.0, status="poison", status_chance=0.3),
    "sludge_bomb": Move("sludge_bomb", "Sludge Bomb", "poison", "special", power=90, accuracy=1.0, status="poison", status_chance=0.3),
    "bug_bite": Move("bug_bite", "Bug Bite", "bug", "physical", power=60, accuracy=1.0),
    "signal_beam": Move("signal_beam", "Signal Beam", "bug", "special", power=75, accuracy=1.0),
}


TYPE_SIGNATURE_MOVES: Dict[str, List[str]] = {
    "grass": ["tackle", "vine_whip", "razor_leaf", "sleep_powder"],
    "fire": ["scratch", "ember", "flame_wheel", "will_o_wisp"],
    "water": ["tackle", "water_gun", "bubble_beam", "aqua_tail"],
    "electric": ["quick_attack", "thunder_shock", "spark", "thunder_wave"],
    "normal": ["tackle", "quick_attack", "bite", "slam"],
    "flying": ["tackle", "gust", "quick_attack", "air_slash"],
    "poison": ["poison_sting", "tackle", "sludge_bomb"],
    "bug": ["tackle", "bug_bite", "signal_beam"],
    "psychic": ["confusion", "psybeam", "future_sight"],
    "fighting": ["karate_chop", "low_sweep", "vital_throw"],
    "fairy": ["disarming_voice", "dazzling_gleam", "moonblast"],
    "dragon": ["dragon_rage", "slam"],
    "dark": ["bite", "slam"],
}


def get(key: str) -> Optional[Move]:
    return MOVES.get(key)


def as_list(keys: Iterable[str]) -> List[Move]:
    return [move for key in keys if (move := MOVES.get(key))]
