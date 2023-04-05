import discord
from discobot_modules.graphics import moon_bar
from db import USERS
import classes

"""
This module defines all the embeds that the bot can display.

An embed is a panel with information arranged hierarchically.
"""

############################
# Help Embeds
############################

def help():
    desc = "To get started, ping the bot!"
    em = discord.Embed(title="POKEBOT 0.1", description=desc, color=0xA0A1B0)
    em.set_thumbnail(url="https://i.pinimg.com/originals/05/51/f5/0551f506725ac1deeaa85d46f8b9a5fd.jpg")
    em.add_field(name="Earn Battle Points", value="Chatting in the server can earn you BP!")
    em.add_field(name="Find Wild Pokemon", value="Occasionally, wild pokemon will spawn. Will you be the one to catch it?")
    em.add_field(name="!shop", value="Show the shop screen, so you can buy items.", inline=False)
    em.add_field(name="!pokedex", value="View the pokedex. Type !pokedex 151 to see a specific pokemon.")
    em.add_field(name="!summary", value="Take a look at your own pokemon. type a number to see a specific one of your mons.")
    #em.add_field(name="!leaderboard", value="Display the leaderboard of today's top players.")
    return em

def admin_help():
    desc = "Here are some of the admin's commands."
    em = discord.Embed(title="ADMIN DASHBOARD WIP", description=desc, color=0xA0A1B0)
    em.set_thumbnail(url="https://cdn.discordapp.com/attachments/402334732974686208/1079251418340409465/3t0f5yfuwaka1.jpg")
    em.add_field(name="!save", value="Save the database.")
    em.add_field(name="\"]\", \"die\", \"kill\"", value="Save and shutdown.")
    #em.add_field(name="!save", value="Save the database.")
    #em.add_field(name="!grant", value="Grant a user a specific character.")
    #em.add_field(name="!pay", value="Give a user some gold. can be negative.")
    #em.add_field(name="!token", value="give a user one spoon token.")
    
    return em

############################
# Profile Embeds
############################

def user_wincount(user):
    total = 0
    for battle in user["battles"]:
        if battle[0] == 1:
            total += 1
    return total

def user_winlossratio(user):
    if len(user["battles"]) == 0:
        return 0 # Divide by zero error protection
    total = 0
    for battle in user["battles"]:
        total += battle[0]
    return total / len(user["battles"])

def profile(user):
    
    udic = USERS[user.id]
    bp = udic["bp"]
    wins = user_wincount(udic)
    wlr = user_winlossratio(udic)
    #chars = udic["chars"]
    desc = f":coin:{bp}\n:trophy:{wins}\n:lifter:{wlr}"
    em = discord.Embed(title=user.name, description=desc, color=0xA0A1B0)
    em.set_thumbnail(url=user.display_avatar.url)
    pkmn = ""
    for i, mon in enumerate(USERS[user.id]["pokemon"]):
        mymon = classes.Individual.from_dict(mon)
        pkmn += mymon.get_name()
        pkmn += "\n"
        if i > 5:
            break
    pkmn = pkmn if pkmn else "None."
    em.add_field(name="Pokemon:", value=pkmn)
    return em


############################
# Pokemon Embeds
############################

def stat_blocks(pokemon):
    # define helpful lists
    colors = [
        "⬛",
        "🟥",
        "🟧",
        "🟨",
        "🟩",
        "🟦",
    ]
    stats = pokemon.get_stats_list()
    names = [
        "HP",
        "ATK",
        "DEF",
        "SPATK",
        "SPDEF",
        "SPEED"
    ]
    # Original stats
    values = stats.copy()
    # Round stats by dividing by 50
    stats = [int(round(x/50)) for x in stats]
    # Add a line to the string for each stat.
    text = ""
    for stat, name, value in zip(stats, names, values):
        text += name + " "
        # add a certain amount of blocks.
        # Add 1 if the value is rounded to 0.
        blocks = max(stat,1)
        for i in range(blocks):
            text += colors[stat]
        #text += str(value)
        text += "\n"
    return text
    

def pokedex(pokemon_id):
    # bounds checks
    pokemon_id = pokemon_id % 890
    if pokemon_id < 1:
        pokemon_id = 890
    
    pkmn = classes.Species.load_index(pokemon_id)
    title= f"{pkmn.name} #{pokemon_id}"
    poketypes = pokemon_instance.species.get_elemental_typing()
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
    return em
    


############################
# interaction Embeds
############################

def inventory():
    desc = "More items coming soon!"
    em = discord.Embed(title="POKEBOT SHOP", description=desc, color=0xA0A1B0)
    em.set_thumbnail(url="https://i.pinimg.com/originals/05/51/f5/0551f506725ac1deeaa85d46f8b9a5fd.jpg")
    em.add_field(name="<:poke:1092956340349046844> Pokeball BP10", value="Normal catch rate.\n!buy pokeball")
    em.add_field(name="<:great:1092956339166248961> Greatball BP20", value="1.5x catch rate.\n!buy greatball")
    em.add_field(name="<:ultra:1092956341670252624> Ultraball BP30", value="2x catch rate.\n!buy ultraball")
    return em


############################
# Pokemon Event Embeds
############################

def wild_encounter(pkmn):
    status = "" if pkmn.species.status == "Normal" else pkmn.species.status
    if pkmn.shiny:
        status = "SHINY"
    title= f"WILD {status} ENCOUNTER"
    pokestats = stat_blocks(pkmn)
    desc = f"**A wild {pkmn.species.name} appeared!**"
    em = discord.Embed(title=title, description=desc, color=0xE12005)
    em.set_image(url=pkmn.species.naive_image())
    return em
    
def battle(battle):
    # Not yet implemented.
    ...

############################
# Leaderboard Embeds
############################


def leaderboard(title, desc, sortingfunc, key, emoji, length=10, color=0x606170):
    # Sort leaderboard by specific topic
    sorted_udex = sorted(USERS.cache.items(), key=sortingfuc, reverse=True)
    
    # Create embed
    em = discord.Embed(title=title, description=desc, color=color, url="")

    for uid, user in sorted_udex:
        em.add_field(name=user["name"], value=emoji+str(user[key]), inline=False)
        if len(em.fields) == length:
            break
    return em


def leaderboard_bp():
    return leaderboard(
                    "RICHEST PLAYERS", 
                    "Some of the most active users today...",
                    lambda x: x[1]["bp"],
                    ":coin:"
                    )

def leaderboard_most_mons():
    return leaderboard(
                    "POKEMON COLLECTORS", 
                    "Some of the most active users today...",
                    lambda x: len(x[1]["pokemon"]),
                    "<:poke:1092956340349046844>"
                    )
                    
def leaderboard_wins():
    return leaderboard(
                    "BIGGEST FIGHTERS", 
                    "Some of the most active users today...",
                    lambda x: user_wincount(x[1]),
                    ":trophy:"
                    )

def leaderboard_wlr():
    return leaderboard(
                    "EXPERT BATTLERS", 
                    "Some of the most active users today...",
                    lambda x: user_winlossratio(x[1]),
                    ":lifter:"
                    )
