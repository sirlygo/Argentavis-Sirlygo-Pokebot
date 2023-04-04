import discord
import random

import discobot_modules.action_timers as at
import discobot_modules.emoji_actions as ea
import discobot_modules.dice as dice
import discobot_modules.egg as egg
from discobot_modules.pretty_disco import pretty_listen
import discobot_modules.text_coloring as tc

import embeds
import users
import db


import classes

print("Modules Imported.")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents = intents)

home_channel = None


@client.event
async def on_ready():
    msg = "Pokebot active."
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
    
    #ping the bot
    if msgl.split()[0] == client.user.mention:
        await users.profile(message)

    if msgl.split()[0] == "!roll":
        await dice.roll(message)

    if msgl.split()[0] == "!egg":
        await egg.egg_timer(message)
        
    
    
    if msgl.split()[0] == "!makpkmn":
        
        spec = classes.Species.from_file(int(msgl.split()[2]))
        
        newmon = classes.Individual(msgl.split()[1], spec)
        
        db.USERS[message.author.id]["pokemon"].append(newmon.to_dict())
        
    if msgl.split()[0] == "!pokedex":
        
        await message.reply(embed = embeds.pokedex(int(msgl.split()[1])))
    
    # Award bp to chatters.
    if message.author.id in db.USERS:
        frequency = 1.0
        if random.random() <= frequency:
            db.USERS[message.author.id]["bp"] += 1
    
    
    admin_uids = [145031705303056384]
    
    if message.author.id in admin_uids:
        print("__--~~ADMIN SPEAKING~~--__")
        if msgl.split()[0] == "!save":
            db.save_db()
            await message.channel.send("Saved database.")
        if msgl.split()[0] in ["]", "die", "kill"]:
            await message.channel.send("Saving database and killing bot process...")
            db.save_db()
            quit()
        
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