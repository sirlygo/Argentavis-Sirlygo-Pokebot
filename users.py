from __future__ import annotations

import math
import time
from typing import Dict, List, Optional, Sequence, Tuple

import classes
from db import USERS
import embeds

STAT_DISPLAY = {
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "sp_attack": "Sp. Atk",
    "sp_defense": "Sp. Def",
    "speed": "Speed",
}

STAT_ALIASES = {
    "hp": "hp",
    "health": "hp",
    "atk": "attack",
    "attack": "attack",
    "def": "defense",
    "defense": "defense",
    "spd": "speed",
    "spe": "speed",
    "speed": "speed",
    "spa": "sp_attack",
    "spatk": "sp_attack",
    "sp_atk": "sp_attack",
    "specialattack": "sp_attack",
    "spdef": "sp_defense",
    "sp_def": "sp_defense",
    "specialdefense": "sp_defense",
}

TRAINING_COST = 5

"""This module handles user profiles, onboarding, and party management."""


def ensure_user_record(uid: int) -> Dict:
    """Ensure that a user record contains the latest structural fields."""
    if uid not in USERS:
        raise KeyError(f"User {uid} not found in database.")

    user = USERS[uid]
    changed = False

    if user.get("uid") != uid:
        user["uid"] = uid
        changed = True
    if "name" not in user:
        user["name"] = str(uid)
        changed = True
    if "bp" not in user:
        user["bp"] = 0
        changed = True
    if "items" not in user or not isinstance(user["items"], dict):
        user["items"] = {}
        changed = True
    if "pokemon" not in user or not isinstance(user["pokemon"], list):
        user["pokemon"] = []
        changed = True

    roster = user["pokemon"]
    ids_seen = set()
    for idx, data in enumerate(list(roster)):
        mon = classes.Individual.from_dict(data)
        if not mon:
            continue
        serialised = mon.to_dict()
        if serialised != data:
            roster[idx] = serialised
            changed = True
        ids_seen.add(serialised["uid"])

    if "party" not in user or not isinstance(user["party"], list):
        user["party"] = []
        changed = True

    filtered_party = [pid for pid in user["party"] if pid in ids_seen]
    if filtered_party != user["party"]:
        user["party"] = filtered_party
        changed = True

    if not user["party"] and roster:
        user["party"] = [entry.get("uid") for entry in roster[:6] if entry.get("uid")]
        changed = True

    if "battles" not in user or not isinstance(user["battles"], list):
        user["battles"] = []
        changed = True

    if changed:
        USERS[uid] = user
        USERS.save_item(uid)

    return user


def update_display_name(member) -> None:
    """Persist the latest display name for leaderboard and embeds."""
    if not member or member.id not in USERS:
        return
    display_name = getattr(member, "display_name", None) or getattr(member, "name", None)
    if not display_name:
        return
    user = ensure_user_record(member.id)
    if user.get("name") != display_name:
        user["name"] = display_name
        USERS[member.id] = user
        USERS.save_item(member.id)


def get_display_name(uid: int) -> str:
    user = ensure_user_record(uid)
    return user.get("name", str(uid))


def roster_with_ids(uid: int) -> List[Tuple[str, classes.Individual]]:
    user = ensure_user_record(uid)
    roster: List[Tuple[str, classes.Individual]] = []
    for data in user["pokemon"]:
        mon = classes.Individual.from_dict(data)
        if mon:
            roster.append((mon.instance_id, mon))
    return roster


def get_party_members(uid: int) -> List[classes.Individual]:
    user = ensure_user_record(uid)
    roster_map = {mon_id: mon for mon_id, mon in roster_with_ids(uid)}
    party_members: List[classes.Individual] = []
    for mon_id in user.get("party", []):
        mon = roster_map.get(mon_id)
        if mon:
            party_members.append(mon)
    return party_members


def add_to_party(uid: int, index: int) -> Tuple[bool, str]:
    roster = roster_with_ids(uid)
    if not roster:
        return False, "You haven't caught any Pokémon yet. Try catching a wild one first!"
    if index < 1 or index > len(roster):
        return False, "That Pokémon index is out of range."
    mon_id, mon = roster[index - 1]
    user = ensure_user_record(uid)
    if mon_id in user["party"]:
        return False, f"{mon.get_title()} is already in your party."
    if len(user["party"]) >= 6:
        return False, "Your party is full. Remove a member first."
    user["party"].append(mon_id)
    USERS[uid] = user
    USERS.save_item(uid)
    return True, f"Added {mon.get_title()} to your party."


def remove_from_party(uid: int, slot: int) -> Tuple[bool, str]:
    user = ensure_user_record(uid)
    party = user.get("party", [])
    if not party:
        return False, "Your party is already empty."
    if slot < 1 or slot > len(party):
        return False, "That party slot doesn't exist yet."
    mon_id = party.pop(slot - 1)
    removed_mon: Optional[classes.Individual] = None
    for data in user["pokemon"]:
        if data.get("uid") == mon_id:
            removed_mon = classes.Individual.from_dict(data)
            break
    USERS[uid] = user
    USERS.save_item(uid)
    if removed_mon:
        return True, f"Removed {removed_mon.get_title()} from your party."
    return True, "Removed that party member."


def swap_party_members(uid: int, slot_a: int, slot_b: int) -> Tuple[bool, str]:
    user = ensure_user_record(uid)
    party = user.get("party", [])
    size = len(party)
    if size < 2:
        return False, "You need at least two party members to swap them."
    if not (1 <= slot_a <= size and 1 <= slot_b <= size):
        return False, "One of those party slots doesn't exist yet."
    if slot_a == slot_b:
        return False, "Those slots are the same Pokémon already."
    party[slot_a - 1], party[slot_b - 1] = party[slot_b - 1], party[slot_a - 1]
    USERS[uid] = user
    USERS.save_item(uid)
    return True, "Swapped those party members."


def auto_fill_party(uid: int) -> Tuple[bool, str]:
    roster = roster_with_ids(uid)
    if not roster:
        return False, "You haven't caught any Pokémon yet."
    user = ensure_user_record(uid)
    user["party"] = [mon_id for mon_id, _ in roster[:6]]
    USERS[uid] = user
    USERS.save_item(uid)
    count = min(len(roster), 6)
    return True, f"Filled your party with the first {count} Pokémon in your collection."


def catch_pokemon(uid: int, mon: classes.Individual) -> None:
    user = ensure_user_record(uid)
    user.setdefault("pokemon", []).append(mon.to_dict())
    if len(user.setdefault("party", [])) < 6:
        user["party"].append(mon.instance_id)
    USERS[uid] = user
    USERS.save_item(uid)


def _resolve_stat_key(token: str) -> Optional[str]:
    if not token:
        return None
    normalised = token.replace("-", "").replace("_", "").lower()
    return STAT_ALIASES.get(normalised)


def train_pokemon(uid: int, slot: int, stat_key: str, sessions: int = 1) -> Tuple[bool, str, Optional[classes.Individual]]:
    user = ensure_user_record(uid)
    party = user.get("party", [])
    if not party:
        return False, "You don't have any Pokémon in your party yet.", None
    if slot < 1 or slot > len(party):
        return False, "That party slot doesn't exist yet.", None

    mon_id = party[slot - 1]
    roster = user.get("pokemon", [])
    mon_index: Optional[int] = None
    mon_obj: Optional[classes.Individual] = None
    for idx, entry in enumerate(roster):
        if entry.get("uid") == mon_id:
            mon_index = idx
            mon_obj = classes.Individual.from_dict(entry)
            break
    if mon_index is None or not mon_obj:
        return False, "I couldn't find that Pokémon in your collection.", None

    current = mon_obj.evs.get(stat_key, 0)
    per_stat_cap = 252
    remaining_stat_capacity = max(0, per_stat_cap - current)
    remaining_total_capacity = mon_obj.remaining_ev_capacity()
    if remaining_stat_capacity <= 0:
        return False, f"{mon_obj.get_title()} has already maxed out {STAT_DISPLAY[stat_key]} training.", None
    if remaining_total_capacity <= 0:
        return False, f"{mon_obj.get_title()} has already reached the total EV limit.", None

    sessions = max(1, int(sessions))
    requested_gain = sessions * 4
    gain_cap = min(remaining_stat_capacity, remaining_total_capacity)
    gain = min(requested_gain, gain_cap)
    if gain <= 0:
        return False, f"{mon_obj.get_title()} can't gain any more EVs right now.", None

    sessions_used = max(1, math.ceil(gain / 4))
    cost = sessions_used * TRAINING_COST
    if user.get("bp", 0) < cost:
        plural = "s" if sessions_used != 1 else ""
        return False, f"You need {cost} BP to run {sessions_used} training session{plural}.", None

    mon_obj.evs[stat_key] = min(per_stat_cap, mon_obj.evs.get(stat_key, 0) + gain)
    overflow = mon_obj.total_evs() - 510
    if overflow > 0:
        mon_obj.evs[stat_key] = max(0, mon_obj.evs[stat_key] - overflow)

    user["bp"] = user.get("bp", 0) - cost
    user["pokemon"][mon_index] = mon_obj.to_dict()
    USERS[uid] = user
    USERS.save_item(uid)

    stat_name = STAT_DISPLAY[stat_key]
    stats = mon_obj.get_stats()
    message = (
        f"Trained {mon_obj.get_title()} in {stat_name}! +{gain} EVs ({mon_obj.evs[stat_key]} total) "
        f"for {cost} BP. {stat_name} is now {stats.get(stat_key, 0)}."
    )
    if mon_obj.remaining_ev_capacity() <= 0 or mon_obj.evs[stat_key] >= per_stat_cap:
        message += " They can't train further in that area."

    return True, message, mon_obj


def adjust_bp(uid: int, delta: int) -> int:
    user = ensure_user_record(uid)
    user["bp"] = user.get("bp", 0) + delta
    USERS[uid] = user
    USERS.save_item(uid)
    return user["bp"]


def record_battle(uid: int, outcome: str, context: Dict) -> None:
    if uid not in USERS:
        return
    user = ensure_user_record(uid)
    entry = {"outcome": outcome, "context": context, "timestamp": time.time()}
    user.setdefault("battles", []).append(entry)
    user["battles"] = user["battles"][-50:]
    USERS[uid] = user
    USERS.save_item(uid)


async def train_command(message, args: Sequence[str]):
    uid = message.author.id
    if uid not in USERS:
        new_user(message.author)
    ensure_user_record(uid)
    update_display_name(message.author)

    if len(args) < 2:
        await message.reply(
            "Use `!train <party slot> <stat> [sessions]`, for example `!train 1 attack 3`."
        )
        return

    try:
        slot = int(args[0])
    except ValueError:
        await message.reply("I couldn't understand that party slot number.")
        return

    stat_key = _resolve_stat_key(args[1])
    if not stat_key:
        await message.reply(
            "I couldn't tell which stat you meant. Try HP, Attack, Defense, SpAtk, SpDef, or Speed."
        )
        return

    sessions = 1
    if len(args) >= 3:
        try:
            sessions = max(1, int(args[2]))
        except ValueError:
            await message.reply("I couldn't understand how many training sessions to run.")
            return
        sessions = min(sessions, 63)

    success, response, mon = train_pokemon(uid, slot, stat_key, sessions)
    if not success:
        await message.reply(response)
        return

    embed = embeds.pokemon_summary(mon)
    await message.reply(response, embed=embed)


async def party_command(message, args: Sequence[str]):
    uid = message.author.id
    if uid not in USERS:
        new_user(message.author)
    ensure_user_record(uid)
    update_display_name(message.author)

    response = ""
    if not args:
        response = "Use `!party add <number>` to move a Pokémon from your collection into your party."
    else:
        action = args[0].lower()
        if action == "add" and len(args) >= 2:
            try:
                index = int(args[1])
            except ValueError:
                response = "I couldn't understand that collection number."
            else:
                _, response = add_to_party(uid, index)
        elif action in {"remove", "rm", "drop"} and len(args) >= 2:
            try:
                slot = int(args[1])
            except ValueError:
                response = "I couldn't understand that party slot."
            else:
                _, response = remove_from_party(uid, slot)
        elif action == "swap" and len(args) >= 3:
            try:
                slot_a = int(args[1])
                slot_b = int(args[2])
            except ValueError:
                response = "I couldn't understand one of those party slots."
            else:
                _, response = swap_party_members(uid, slot_a, slot_b)
        elif action in {"auto", "fill"}:
            _, response = auto_fill_party(uid)
        else:
            response = "Try `!party`, `!party add 3`, `!party remove 1`, `!party swap 1 3`, or `!party auto`."

    party_members = get_party_members(uid)
    roster_members = [mon for _, mon in roster_with_ids(uid)]
    embed = embeds.party(message.author, party_members, roster_members, note=response)
    await message.reply(embed=embed)


async def profile(message):
    """Show a profile, making a new user if needed."""
    new = False
    if message.author.id not in USERS:
        new_user(message.author)
        new = True
    ensure_user_record(message.author.id)
    update_display_name(message.author)
    tosay = "Welcome to the community!" if new else ""
    await message.reply(tosay, embed=embeds.profile(message.author))


def new_user(user) -> None:
    # Possibly using a class in addition to this
    # might help with if i ever must change the user struct?
    u = {}
    u["uid"] = user.id

    # Persist a readable name for embeds such as leaderboards.
    display_name = getattr(user, "display_name", None) or getattr(user, "name", None)
    u["name"] = display_name or str(user.id)

    u["bp"] = 0

    u["items"] = {"pokeball": 5}

    u["pokemon"] = []
    u["party"] = []

    u["battles"] = []

    USERS[user.id] = u
    USERS.save_item(user.id)
