from __future__ import annotations

from typing import Dict, Optional, Tuple


LEVEL_EVOLUTIONS: Dict[int, Tuple[int, int]] = {
    1: (16, 2),
    2: (32, 3),
    4: (16, 5),
    5: (36, 6),
    7: (16, 8),
    8: (36, 9),
    10: (7, 11),
    11: (10, 12),
    13: (7, 14),
    14: (10, 15),
    16: (18, 17),
    17: (36, 18),
    19: (20, 20),
    25: (30, 26),
    35: (35, 36),
    39: (30, 40),
    52: (28, 53),
    58: (35, 59),
    63: (16, 64),
    64: (36, 65),
    66: (28, 67),
    67: (40, 68),
}


def next_evolution(species_id: int, level: int) -> Optional[int]:
    entry = LEVEL_EVOLUTIONS.get(int(species_id))
    if not entry:
        return None
    required_level, evolved_species = entry
    if level >= required_level:
        return evolved_species
    return None
