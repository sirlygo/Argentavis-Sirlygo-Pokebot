import discord

from discobot_modules.graphics import moon_bar
from db import USERS
from db import ITEMS
import classes
from economy import user_item_count
from pathlib import Path
from typing import Iterable, List, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from battle import BattleParticipant, BattleResult

"""
This module defines all the embeds that the bot can display.

An embed is a panel with information arranged hierarchically.
"""

STAT_ORDER = classes.STAT_KEYS
STAT_LABELS = {
    "hp": "HP",
    "attack": "Attack",
    "defense": "Defense",
    "sp_attack": "Sp. Atk",
    "sp_defense": "Sp. Def",
    "speed": "Speed",
}

############################
# Help Embeds
############################

def help():
    desc = "To get started, ping the bot!"
    em = discord.Embed(title="Mew Pokébot 0.2.0", description=desc, color=0xA0A1B0)
    em.set_thumbnail(url="https://i.pinimg.com/originals/05/51/f5/0551f506725ac1deeaa85d46f8b9a5fd.jpg")
    em.add_field(name="Earn Battle Points", value="Chatting in the server can earn you BP!")
    em.add_field(name="Find Wild Pokemon", value="Occasionally, wild pokemon will spawn. Will you be the one to catch it?")
    em.add_field(name="!shop", value="Show the shop screen, so you can buy items.", inline=False)
    em.add_field(name="!pokedex", value="View the pokedex. Type !pokedex 151 to see a specific pokemon.")
    em.add_field(name="!summary", value="Take a look at your own pokemon. type a number to see a specific one of your mons.")
    em.add_field(name="!party", value="Review and edit your battling party. Try `!party add 3` to add a caught Pokémon.", inline=False)
    em.add_field(name="!train", value="Spend BP to boost your party's stats, e.g. `!train 1 attack`.", inline=False)
    em.add_field(name="!battle", value="Challenge another trainer with your party using `!battle @trainer` and pick moves with the reaction controls.")
    em.add_field(name="!dev", value="Check out the bot creator and read Mew's source code!")
    #em.add_field(name="!leaderboard", value="Display the leaderboard of today's top players.")
    return em

def admin_help():
    desc = "Here are some of the admin's commands."
    em = discord.Embed(title="ADMIN DASHBOARD WIP", description=desc, color=0xA0A1B0)
    em.set_thumbnail(url="https://cdn.discordapp.com/attachments/402334732974686208/1079251418340409465/3t0f5yfuwaka1.jpg")
    em.add_field(name="!save", value="Save the database.")
    em.add_field(name="\"]\", \"die\", \"kill\"", value="Save and shutdown.")
    em.add_field(name="!spawn", value="Forces a pokemon to spawn.")
    em.add_field(name="!makpkmn", value="debug command to generate a pokemon with a certain dexno and nick.")
    #em.add_field(name="!pay", value="Give a user some gold. can be negative.")
    #em.add_field(name="!token", value="give a user one spoon token.")
    return em
    

def plug():
    title = "About the developer"
    desc = "Hi! I'm the one who wrote this bot. I go by Argentavis or Rad_butte, but you can also just call me butte.(he/it/she)"
    desc += "\n I've been writing discord bots since 2021, primarily for gaming, esports, LGBTQ, and streamer communities."
    desc += "\n I primarily write discord bots in discord.py, but i also know Unity and Godot gamedev, and am also learning rust."
    desc += "\n\n I'm an artist at heart: I see coding as a form of art: because any good artist is a problem-solver, \"How can i accomplish *this* as best as possible, or with as little as neccesary?\""
    desc += "\n I also do 2d and 3d art, and am writing short science fiction."
    desc += "\n Hit me up! Rad_Attraction_Towards_Pupper#6806"
    
    em = discord.Embed(title=title, description=desc, color=0xdd0c7f)
    em.set_thumbnail(url="https://img.booru.org/vb//images/6/6163a7412542541f42c5d37823b8ae5815977715.png")
    em.set_author(name="Argentavis/Rad_butte", url="https://buttegay.carrd.co/",icon_url="https://cdn.discordapp.com/attachments/1042247535911239702/1094139001344114688/dog_kek.png")
    em.set_image(url="https://cdn.discordapp.com/attachments/1042247535911239702/1094142289900740679/orcinus.PNG")
    
    em.add_field(name="Want your own custom discord bot?", value="Order my gig on Fiverr!\nhttps://www.fiverr.com/share/ymERYA")
    em.add_field(name="Interested in an art commission, 2d or 3d?", value="Hit me up and tell me more!")
    em.add_field(name="Want to learn how to code?", value="I can teach you how to make your own bot!\nhttps://www.fiverr.com/share/Xj7bPP")
    em.add_field(name="Check out Mew's source code!", value="https://github.com/Rad-Attraction/Argentavis-Sirlygo-Pokebot", inline=False)
    
    return em

############################
# Profile Embeds
############################

def _battle_value(entry) -> float:
    if isinstance(entry, dict):
        outcome = entry.get("outcome")
        if outcome == "win":
            return 1.0
        if outcome == "draw":
            return 0.5
        return 0.0
    if isinstance(entry, (list, tuple)) and entry:
        try:
            return float(entry[0])
        except (TypeError, ValueError):
            return 0.0
    return 0.0


def user_wincount(user):
    total = 0
    for battle in user.get("battles", []):
        if isinstance(battle, dict):
            if battle.get("outcome") == "win":
                total += 1
        elif isinstance(battle, (list, tuple)) and battle:
            if battle[0] == 1:
                total += 1
    return total


def user_winlossratio(user):
    battles = user.get("battles", [])
    if not battles:
        return 0
    total = 0
    for battle in battles:
        total += _battle_value(battle)
    return total / len(battles)

def profile(user):

    udic = USERS[user.id]
    bp = udic.get("bp", 0)
    wins = user_wincount(udic)
    wlr = user_winlossratio(udic)
    desc = f":coin:{bp}\n:trophy:{wins}\n:lifter:{wlr:.2f}"
    title = getattr(user, "display_name", None) or getattr(user, "name", "Trainer")
    em = discord.Embed(title=title, description=desc, color=0xA0A1B0)
    if getattr(user, "display_avatar", None):
        em.set_thumbnail(url=user.display_avatar.url)

    roster_map = {}
    collection = []
    for index, mon_data in enumerate(udic.get("pokemon", []), start=1):
        mon = classes.Individual.from_dict(mon_data)
        if not mon:
            continue
        roster_map[mon_data.get("uid")] = mon
        if len(collection) < 10:
            shiny = " ✨" if mon.shiny else ""
            collection.append(f"{index}. {mon.get_title()}{shiny}")

    party_lines = []
    for idx, mon_id in enumerate(udic.get("party", []), start=1):
        mon = roster_map.get(mon_id)
        if not mon:
            continue
        shiny = " ✨" if mon.shiny else ""
        party_lines.append(f"{idx}. {mon.get_title()} Lv{mon.level}{shiny}")
    party_text = "\n".join(party_lines) if party_lines else "Set your party with `!party add <number>`."

    em.add_field(name="Party", value=party_text, inline=False)

    pkcount = len(roster_map)
    collection_text = "\n".join(collection) if collection else "None yet."
    em.add_field(name=f"Caught Pokémon: {pkcount}", value=collection_text, inline=False)

    em.add_field(name="Items", value="—", inline=False)
    em.add_field(name="<:poke:1092956340349046844> Pokeball", value=str(user_item_count(user.id, "pokeball")))
    em.add_field(name="<:great:1092956339166248961> Greatball", value=str(user_item_count(user.id, "greatball")))
    em.add_field(name="<:ultra:1092956341670252624> Ultraball", value=str(user_item_count(user.id, "ultraball")))

    return em


def party(user, party_members: Sequence[classes.Individual], roster_members: Sequence[classes.Individual], note: str = ""):
    title = getattr(user, "display_name", None) or getattr(user, "name", "Trainer")
    description = note or "Use `!party add <number>` to add Pokémon from your collection."
    em = discord.Embed(title=f"{title}'s Party", description=description, color=0x5B6EE1)

    if getattr(user, "display_avatar", None):
        em.set_thumbnail(url=user.display_avatar.url)

    if party_members:
        lines = []
        for idx, mon in enumerate(party_members, start=1):
            shiny = " ✨" if mon.shiny else ""
            lines.append(f"{idx}. {mon.get_title()} Lv{mon.level}{shiny}")
        em.add_field(name="Active Party", value="\n".join(lines), inline=False)
    else:
        em.add_field(name="Active Party", value="No Pokémon selected. Try `!party add 1`.", inline=False)

    if roster_members:
        lines = []
        for idx, mon in enumerate(roster_members, start=1):
            shiny = " ✨" if mon.shiny else ""
            lines.append(f"{idx}. {mon.get_title()} Lv{mon.level}{shiny}")
            if idx == 20:
                lines.append("…")
                break
        em.add_field(name="Collection", value="\n".join(lines), inline=False)
    else:
        em.add_field(name="Collection", value="You haven't caught any Pokémon yet.", inline=False)

    return em


############################
# Pokemon Embeds
############################

def stat_blocks(pokemon):
    colors = [
        "⬛",
        "🟥",
        "🟧",
        "🟨",
        "🟩",
        "🟦",
    ]
    if isinstance(pokemon, classes.Individual):
        stat_map = pokemon.get_stats()
    else:
        stat_map = dict(zip(STAT_ORDER, pokemon.get_stats_list()))

    labels = {
        "hp": "HP",
        "attack": "ATK",
        "defense": "DEF",
        "sp_attack": "SPATK",
        "sp_defense": "SPDEF",
        "speed": "SPEED",
    }

    text_lines: List[str] = []
    for key in STAT_ORDER:
        value = stat_map.get(key, 0)
        scaled = int(round(value / 50))
        blocks = max(scaled, 1)
        color_index = min(scaled, len(colors) - 1)
        line = labels[key] + " " + colors[color_index] * blocks + f" ({int(value)})"
        text_lines.append(line)
    return "\n".join(text_lines)
    

def pokedex(pokemon_id):
    # bounds checks
    pokemon_id = pokemon_id % 890
    if pokemon_id < 1:
        pokemon_id = 890
    
    pkmn = classes.Species.load_index(pokemon_id)
    title= f"{pkmn.name} #{pokemon_id}"
    poketypes = pkmn.get_elemental_typing()
    poketypes = [x.name for x in poketypes]
    status = "" if pkmn.status == "Normal" else pkmn.status
    status = f"Generation 1 {status}"
    pokestats = stat_blocks(pkmn)
    desc = f"*{pkmn.pokedex_species}\n{status}*\n{poketypes}\n{pokestats}"
    em = discord.Embed(title=title, description=desc, color=0xE12005)
    em.add_field(name="Abilities", value="\n".join(pkmn.get_abilities()))
    em.set_image(url=pkmn.naive_image())
    return em
    
def pokemon_summary(pokemon_instance):
    title = pokemon_instance.get_title()
    desc = f"Level {pokemon_instance.level}"
    if pokemon_instance.shiny:
        desc += "✨"
    poketypes = pokemon_instance.species.get_elemental_typing()
    poketypes = [x.name for x in poketypes]
    pokestats = stat_blocks(pokemon_instance)
    desc += f"\n{poketypes}\n{pokestats}"
    em = discord.Embed(title=title, description=desc, color=0xE12005)
    em.set_image(url=pokemon_instance.species.naive_image())
    if isinstance(pokemon_instance, classes.Individual):
        iv_parts = [f"{STAT_LABELS[key]} {pokemon_instance.ivs[key]}" for key in STAT_ORDER]
        ev_total = pokemon_instance.total_evs()
        ev_parts = [
            f"{STAT_LABELS[key]} {pokemon_instance.evs[key]}"
            for key in STAT_ORDER
            if pokemon_instance.evs.get(key, 0) > 0
        ]
        iv_text = " | ".join(iv_parts)
        ev_text = " | ".join(ev_parts) if ev_parts else "No EV training yet."
        em.add_field(name="IVs", value=iv_text, inline=False)
        em.add_field(name=f"EVs {ev_total}/510", value=ev_text, inline=False)
    return em
    


############################
# interaction Embeds
############################

def shop():
    desc = "More items coming soon!"
    em = discord.Embed(title="POKEBOT SHOP", description=desc, color=0xA0A1B0)
    em.set_thumbnail(url="https://i.pinimg.com/originals/05/51/f5/0551f506725ac1deeaa85d46f8b9a5fd.jpg")
    pb_price = ITEMS["pokeball"]["price"]
    em.add_field(
        name=f"<:poke:1092956340349046844> Poké Ball — {pb_price} BP",
        value="A basic ball with a standard catch rate.\n`!buy pokeball`",
        inline=False,
    )
    gb_price = ITEMS["greatball"]["price"]
    em.add_field(
        name=f"<:great:1092956339166248961> Great Ball — {gb_price} BP",
        value="Higher chance to catch than a Poké Ball.\n`!buy greatball`",
        inline=False,
    )
    ub_price = ITEMS["ultraball"]["price"]
    em.add_field(
        name=f"<:ultra:1092956341670252624> Ultra Ball — {ub_price} BP",
        value="Premium catch rate for tough encounters.\n`!buy ultraball`",
        inline=False,
    )
    potion_price = ITEMS["potion"]["price"]
    em.add_field(
        name=f"🧴 Potion — {potion_price} BP",
        value="Heals 20 HP mid-battle.\n`!buy potion`",
        inline=False,
    )
    super_price = ITEMS["superpotion"]["price"]
    em.add_field(
        name=f"🧴 Super Potion — {super_price} BP",
        value="Heals 50 HP mid-battle.\n`!buy superpotion`",
        inline=False,
    )
    return em


############################
# Pokemon Event Embeds
############################

def wild_encounter(pkmn):
    status = "" if pkmn.species.status == "Normal" else pkmn.species.status
    if pkmn.shiny:
        status = "SHINY"
    title= f"WILD {status} ENCOUNTER"
    desc = f"**A wild {pkmn.species.name} appeared!**\nLevel {pkmn.level}"
    em = discord.Embed(title=title, description=desc, color=0xE12005)
    em.set_image(url=pkmn.species.naive_image())
    return em

def _format_party_block(participant: "BattleParticipant") -> str:
    if not participant.party:
        return "—"
    lines: List[str] = []
    for idx, mon in enumerate(participant.party, start=1):
        shiny = " ✨" if mon.shiny else ""
        lines.append(f"{idx}. {mon.get_title()} Lv{mon.level}{shiny}")
        if len("\n".join(lines)) > 950:
            lines.append("…")
            break
    return "\n".join(lines)


def _chunk_log(lines: Iterable[str], limit: int = 1024) -> List[List[str]]:
    chunks: List[List[str]] = []
    current: List[str] = []
    current_len = 0
    for line in lines:
        addition = len(line) + 1
        if current and current_len + addition > limit:
            chunks.append(current)
            current = []
            current_len = 0
        current.append(line)
        current_len += addition
    if current:
        chunks.append(current)
    return chunks


def battle(result: "BattleResult"):
    challenger, opponent = result.participants
    if result.winner is None:
        outcome = "It's a draw!"
    else:
        winner = result.participants[result.winner]
        outcome = f"{winner.name} wins the battle!"
    battle_type = "Trainer Battle" if result.battle_type == "trainer" else "Wild Encounter"
    color = 0x3B82F6 if result.battle_type == "trainer" else 0xE12005
    desc = f"{challenger.name} vs {opponent.name}\n{outcome}\nType: {battle_type}"
    em = discord.Embed(title="Battle Results", description=desc, color=color)

    log_lines = result.log or ["No events were recorded."]
    for idx, chunk in enumerate(_chunk_log(log_lines), start=1):
        em.add_field(name=f"Log {idx}", value="\n".join(chunk), inline=False)

    em.add_field(name=f"{challenger.name}'s Party", value=_format_party_block(challenger), inline=True)
    em.add_field(name=f"{opponent.name}'s Party", value=_format_party_block(opponent), inline=True)

    if result.rewards:
        rewards_text = []
        for uid, delta in result.rewards.items():
            if delta == 0:
                continue
            if uid == challenger.user_id:
                name = challenger.name
            elif uid == opponent.user_id:
                name = opponent.name
            else:
                name = f"Trainer {uid}"
            sign = "+" if delta >= 0 else ""
            rewards_text.append(f"{name}: {sign}{delta} BP")
        if rewards_text:
            em.add_field(name="Rewards", value="\n".join(rewards_text), inline=False)

    if getattr(result, "experience_log", None):
        lines = []
        for uid, events in result.experience_log.items():
            name = challenger.name if uid == challenger.user_id else opponent.name if uid == opponent.user_id else f"Trainer {uid}"
            for event in events:
                lines.append(f"{name}: {event}")
        if lines:
            em.add_field(name="Experience", value="\n".join(lines[:10]), inline=False)

    em.set_footer(text=f"Rounds fought: {result.rounds}")
    return em

############################
# Leaderboard Embeds
############################


def _all_users():
    users = []
    seen = set()
    # Include any users already cached in memory.
    for uid, data in USERS.cache.items():
        users.append((uid, data))
        seen.add(uid)

    # Load any remaining users from disk.
    directory = Path(USERS.path_prefix)
    if directory.exists():
        for file in directory.glob("*.json"):
            key = file.stem
            try:
                key = int(key)
            except ValueError:
                pass
            if key in seen:
                continue
            try:
                users.append((key, USERS[key]))
            except FileNotFoundError:
                continue
    return users


def leaderboard(title, desc, sortingfunc, value_func, emoji, length=10, color=0x606170):
    # Sort leaderboard by specific topic
    sorted_udex = sorted(_all_users(), key=sortingfunc, reverse=True)

    # Create embed
    em = discord.Embed(title=title, description=desc, color=color, url="")

    for uid, user in sorted_udex:
        display_name = user.get("name", f"User {uid}")
        value = value_func(uid, user)
        em.add_field(name=display_name, value=f"{emoji} {value}", inline=False)
        if len(em.fields) == length:
            break

    if len(em.fields) == 0:
        em.add_field(name="No trainers found", value="Start chatting to appear on the leaderboard!", inline=False)
    return em


def leaderboard_bp():
    return leaderboard(
                    "RICHEST PLAYERS",
                    "Some of the most active users today...",
                    lambda x: x[1].get("bp", 0),
                    lambda _uid, user: user.get("bp", 0),
                    ":coin:"
                    )

def leaderboard_most_mons():
    return leaderboard(
                    "POKEMON COLLECTORS",
                    "Some of the most active users today...",
                    lambda x: len(x[1].get("pokemon", [])),
                    lambda _uid, user: len(user.get("pokemon", [])),
                    "<:poke:1092956340349046844>"
                    )

def leaderboard_wins():
    return leaderboard(
                    "BIGGEST FIGHTERS",
                    "Some of the most active users today...",
                    lambda x: user_wincount(x[1]),
                    lambda _uid, user: user_wincount(user),
                    ":trophy:"
                    )

def leaderboard_wlr():
    return leaderboard(
                    "EXPERT BATTLERS",
                    "Some of the most active users today...",
                    lambda x: user_winlossratio(x[1]),
                    lambda _uid, user: f"{user_winlossratio(user):.2f}",
                    ":lifter:"
                    )
