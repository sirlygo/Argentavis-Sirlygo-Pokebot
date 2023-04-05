import random

import discobot_modules.emoji_actions
from discobot_modules.emoji_actions import Emoji_Action as ea
from discobot_modules.emoji_actions import action_button_list
from discobot_modules.emoji_actions import ea_response as er

import classes
import embeds
import db


async def roll_possible_encounter(message, probability):
    if random.random() <= probability:
        await new_encounter(message)



    

async def new_encounter(message):
    mon = classes.random_encounter()
    em = embeds.wild_encounter(mon)
    
    encounter_message = await message.reply(embed = em)
    async def fight(args):
        reactor = args[1]
        if reactor.id not in db.USERS:
            await encounter_message.channel.send(f"{reactor.mention}, you need to ping the bot to set up first!")
            return er(complete_action=False)
        await encounter_message.channel.send(f"Battle system not yet implemented ¯\_(ツ)_/¯")
        return er(remove_dis_post=True)
    
    async def catch(args):
        reactor = args[1]
        if reactor.id not in db.USERS:
            await encounter_message.channel.send(f"{reactor.mention}, you need to ping the bot to set up first!")
            return er(complete_action=False)
        db.USERS[reactor.id]["pokemon"].append(mon.to_dict())
        await encounter_message.channel.send(f"Congratulations, {reactor.mention}, you caught {mon.name}!")
        return er(remove_dis_post=True)
    
    a_list = []
    ico = "⚔"
    name = "Fight"
    a = ea(ico, name, fight, pass_user=True)
    a_list.append(a)
    
    ico = "<:poke:1092956340349046844>"
    name = "Pokeball"
    a = ea(ico, name, catch, pass_user=True)
    a_list.append(a)
    ico = "<:great:1092956339166248961>"
    name = "Greatball"
    a = ea(ico, name, catch, pass_user=True)
    a_list.append(a)
    ico = "<:ultra:1092956341670252624>"
    name = "Ultraball"
    a = ea(ico, name, catch, pass_user=True)
    a_list.append(a)
    
    await action_button_list(encounter_message, a_list)