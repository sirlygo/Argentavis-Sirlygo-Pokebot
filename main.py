import discord
import random

import discobot_modules.action_timers as at
import discobot_modules.emoji_actions as ea
import discobot_modules.dice as dice
import discobot_modules.egg as egg
from discobot_modules.pretty_disco import pretty_listen
import discobot_modules.text_coloring as tc

import classes
import embeds
import users
import db
import encounters
import economy



print("Modules Imported.")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents = intents)

home_channel = 1093393965539139644


@client.event
async def on_ready():
    msg = "Mew pokebot active."
    print(msg)
    if home_channel:
        await client.get_channel(home_channel).send(msg)
    await at.iterate_timers()

@client.event
async def on_reaction_add(reaction, user):
    if True:
        print(reaction.emoji)

    #ignore all reactions from the bot itself
    if (user == client.user):
        return

    await ea.action_listen_list(reaction, user)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
        pass

    msg = message.content
    msgl = msg.lower()
    
    if msgl == "": # Handle image-only messages
        msgl = "."
    
    if msgl.split()[0] == "!hello":
        await message.channel.send("hi :)")
        
    if msgl.split()[0] == "!help":
        await message.reply(embed = embeds.help())
    
    if msgl.split()[0] in ["!dev", "!github", "!source", "!comms", "!plug", "!shamelessplug", "!butte", "!gay"]:
        await message.reply(embed = embeds.plug())
    
    
    #ping the bot
    if msgl.split()[0] == client.user.mention:
        await users.profile(message)

    if msgl.split()[0] == "!roll":
        await dice.roll(message)

    if msgl.split()[0] == "!egg":
        await egg.egg_timer(message)
    
    if msgl.split()[0] == "!shop":
        await economy.send_shop_screen(message)
        
    if msgl.split()[0] == "!buy":
        if msgl.split()[1] in ["pokeball", "greatball", "ultraball"]:
            await economy.buy(message, msgl.split()[1])
            
    if msgl.split()[0] == "!pokedex":
        await message.reply(embed = embeds.pokedex(int(msgl.split()[1])))
        
    if msgl.split()[0] == "!summary":
        index = 0
        if msgl.split()[1].isdigit():
            index = int(msgl.split()[1])
        pkmn = classes.Individual.from_dict(db.USERS[message.author.id]["pokemon"][index])
        await message.reply(embed = embeds.pokemon_summary(pkmn))
    
    # Award bp to chatters.
    if message.author.id in db.USERS:
        frequency = 1.0
        if random.random() <= frequency:
            db.USERS[message.author.id]["bp"] += 1
    
    # Random Spawns
    SPAWN_RATE = 0.02
    
    if home_channel:
        channel = client.get_channel(home_channel)
        await encounters.roll_possible_encounter(channel, SPAWN_RATE)
    else:
        await encounters.roll_possible_encounter(message.channel, SPAWN_RATE)
    
    admin_uids = [145031705303056384, 291107598030340106]
    
    if message.author.id in admin_uids:
        print("__--~~ADMIN SPEAKING~~--__")
        if msgl == "!admin help":
            await message.reply(embed = embeds.help())
        if msgl.split()[0] == "!save":
            db.save_db()
            await message.channel.send("Saved database.")
        if msgl.split()[0] in ["]", "die", "kill"]:
            await message.channel.send("Saving database and killing bot process...")
            db.save_db()
            quit()
        if msgl.split()[0] == "!makpkmn":
            
            spec = classes.Species.load_index(int(msgl.split()[1]))
            
            newmon = classes.Individual(spec, nickname=msgl.split()[2])
            
            db.USERS[message.author.id]["pokemon"].append(newmon.to_dict())
        if msgl.split()[0] == "!spawn":
            await encounters.roll_possible_encounter(message.channel, 1)
    
    # memes
    if msgl == "mew come here":
        await message.channel.send("https://www.youtube.com/watch?v=krKfi0voUGA")
    
    
    
    pretty_listen(message)
    await at.listen_timers(message)


def login():
    try:
        #closes the file after the with block
        with open("token", "r+") as keyfile:
            key = keyfile.read()
            client.run(key)
    except OSError:
        print(f"\n\n{tc.R}WARNING: RUNNING BOT FAILED.\n\n{tc.O}There was an error opening the token file. Make sure you have the token file in the right directory. if you don't have one, create a discord bot in the discord developer portal. {tc.W}\n\n")
        raise OSError
    except Exception:
        print(f"\n\n{tc.R}WARNING: RUNNING BOT FAILED.\n\n{tc.O}There was an error connecting to discord for some reason. {tc.W}\n\n")
        raise Exception
        
if __name__ == "__main__":
    # Call login only if this file is being run on its own.
    login()