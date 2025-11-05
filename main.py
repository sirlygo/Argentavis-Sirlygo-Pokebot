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
import battle



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

    parts = msgl.split()
    command = parts[0]
    args = parts[1:]

    author_id = message.author.id
    award_chat_bp = True
    if author_id not in db.USERS:
        users.new_user(message.author)
    users.ensure_user_record(author_id)
    users.update_display_name(message.author)

    if command == "!hello":
        await message.channel.send("hi :)")

    if command == "!help":
        await message.reply(embed = embeds.help())

    if command in ["!dev", "!github", "!source", "!comms", "!plug", "!shamelessplug", "!butte", "!gay"]:
        await message.reply(embed = embeds.plug())


    #ping the bot
    if command == client.user.mention:
        await users.profile(message)

    if command == "!roll":
        await dice.roll(message)

    if command == "!egg":
        await egg.egg_timer(message)

    if command == "!shop":
        await economy.send_shop_screen(message)

    if command == "!buy":
        if not args:
            await message.reply("What would you like to buy? Try `!buy pokeball`.")
        else:
            item_key = args[0].lower()
            if item_key in ["pokeball", "greatball", "ultraball", "potion", "superpotion"]:
                await economy.buy(message, item_key)
            else:
                await message.reply("That item isn't in stock right now.")

    if command == "!pokedex":
        if not args:
            await message.reply("Please specify a Pokédex number, e.g. `!pokedex 151`.")
        else:
            try:
                await message.reply(embed = embeds.pokedex(int(args[0])))
            except ValueError:
                await message.reply("I couldn't understand that Pokédex number.")

    if command == "!summary":
        index = 1
        if args and args[0].isdigit():
            index = int(args[0])
        if index <= 0:
            await message.reply("Pokémon numbers start at 1.")
            return
        try:
            user = db.USERS[author_id]
            pokemon_list = user["pokemon"]
            if not pokemon_list:
                await message.reply("You haven't caught any Pokémon yet!")
                return
            if index > len(pokemon_list):
                await message.reply("You don't have that many Pokémon yet.")
                return
            pkmn = classes.Individual.from_dict(pokemon_list[index - 1])
            if not pkmn:
                raise ValueError
        except (KeyError, IndexError, ValueError):
            await message.reply("I couldn't find that Pokémon in your collection.")
            return
        await message.reply(embed=embeds.pokemon_summary(pkmn))

    if command == "!party":
        await users.party_command(message, args)

    if command == "!train":
        await users.train_command(message, args)

    if command == "!leaderboard":
        board_key = args[0] if args else "bp"
        boards = {
            "bp": embeds.leaderboard_bp,
            "mons": embeds.leaderboard_most_mons,
            "pokemon": embeds.leaderboard_most_mons,
            "wins": embeds.leaderboard_wins,
            "wlr": embeds.leaderboard_wlr,
        }
        board_func = boards.get(board_key)
        if board_func:
            await message.reply(embed = board_func())
        else:
            await message.reply("Unknown leaderboard. Try `bp`, `mons`, `wins`, or `wlr`.")

    if command == "!battle":
        award_chat_bp = False
        if not message.mentions:
            await message.reply("You need to mention a trainer to battle, e.g. `!battle @Mew`.")
        else:
            opponent = message.mentions[0]
            if opponent.id == author_id:
                await message.reply("You can't battle yourself!")
            elif opponent.bot:
                await message.reply("Battling bots isn't supported yet.")
            else:
                if opponent.id not in db.USERS:
                    users.new_user(opponent)
                users.ensure_user_record(opponent.id)
                users.update_display_name(opponent)
                challenger_party = users.get_party_members(author_id)
                if not challenger_party:
                    await message.reply("Set up a party with `!party add <number>` before battling!")
                else:
                    opponent_party = users.get_party_members(opponent.id)
                    if not opponent_party:
                        await message.reply(f"{opponent.mention} doesn't have a party ready yet.")
                    else:
                        await battle.start_trainer_battle(
                            message,
                            author_id,
                            getattr(message.author, "display_name", message.author.name),
                            challenger_party,
                            opponent.id,
                            getattr(opponent, "display_name", opponent.name),
                            opponent_party,
                        )

    # Award bp to chatters.
    if award_chat_bp:
        frequency = 1.0
        if random.random() <= frequency:
            users.adjust_bp(author_id, 1)
    
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
        if command == "!save":
            db.save_db()
            await message.channel.send("Saved database.")
        if command in ["]", "die", "kill"]:
            await message.channel.send("Saving database and killing bot process...")
            db.save_db()
            quit()
        if command == "!makpkmn" and len(args) >= 2:
            spec = classes.Species.load_index(int(args[0]))
            newmon = classes.Individual(spec, nickname=args[1])
            db.USERS[message.author.id]["pokemon"].append(newmon.to_dict())
            db.USERS.save_item(message.author.id)
        if command == "!spawn":
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