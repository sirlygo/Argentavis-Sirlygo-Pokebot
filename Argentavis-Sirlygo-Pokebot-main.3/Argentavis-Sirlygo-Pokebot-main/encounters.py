import random

import discobot_modules.emoji_actions
from discobot_modules.emoji_actions import Emoji_Action as ea
from discobot_modules.emoji_actions import action_button_list
from discobot_modules.emoji_actions import ea_response as er

from db import USERS
from db import ITEMS

import classes
import embeds
import economy

"""
This class handles the behavior of the wild encounter system.
"""


async def roll_possible_encounter(channel, probability):
    if random.random() <= probability:
        await new_encounter(channel)



async def new_encounter(channel):
    mon = classes.random_encounter()
    em = embeds.wild_encounter(mon)

    encounter_message = await channel.send(embed = em)
    async def fight(args):
        reactor = args[1]
        if reactor.id not in USERS:
            await encounter_message.channel.send(f"{reactor.mention}, you need to ping the bot to set up first!")
            return er(complete_action=False)
        await encounter_message.channel.send(f"Battle system not yet implemented ¯\_(ツ)_/¯")
        return er(complete_action=False)
        #return er(remove_dis_post=True, clear_reactions=True)

    async def catch(args, ball = "pokeball"):
        reactor = args[1]
        if reactor.id not in USERS:
            await encounter_message.channel.send(f"{reactor.mention}, you need to ping the bot to set up first!")
            return er(complete_action=False)

        has_ball = economy.user_spend_item(reactor.id, ball)
        ballname = ITEMS[ball]["name"]
        if not has_ball:
            await encounter_message.channel.send(f"{reactor.mention}, you don't have any {ballname}s!")
            return er(complete_action=False)
        probability = float(mon.species.catch_rate) / 255.0
        catch = random.random() <= probability*ITEMS[ball]["catch_rate"]
        if catch:
            USERS[reactor.id]["pokemon"].append(mon.to_dict())
            USERS.save_item(reactor.id)
            await encounter_message.channel.send(f"Congratulations, {reactor.mention}, you caught {mon.get_name()}!")
            return er(remove_dis_post=True, clear_reactions=True)
        else:
            await encounter_message.channel.send(f"Oh! {reactor.mention}, the wild {mon.get_name()} broke out of the {ballname}!")
            return er(complete_action=False)

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
    a = ea(ico, name, lambda a: catch(a, "greatball"), pass_user=True)
    a_list.append(a)
    ico = "<:ultra:1092956341670252624>"
    name = "Ultraball"
    a = ea(ico, name, lambda a: catch(a, "ultraball"), pass_user=True)
    a_list.append(a)

    await action_button_list(encounter_message, a_list)