from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import discord

from discobot_modules import emoji_actions
from discobot_modules.emoji_actions import Emoji_Action, ea_response

from db import ITEMS

import classes
import moves
import embeds
import users
import economy


@dataclass
class BattleParticipant:
    user_id: Optional[int]
    name: str
    party: Sequence[classes.Individual]


@dataclass
class QueuedAction:
    kind: str
    move: Optional[moves.Move] = None
    switch_index: Optional[int] = None
    item_key: Optional[str] = None
    flee: bool = False


@dataclass
class BattlePokemonState:
    individual: classes.Individual
    current_hp: int = field(init=False)
    status: Optional[str] = None
    status_turns: int = 0
    participated: bool = False

    def __post_init__(self) -> None:
        self.current_hp = self.individual.max_hp()

    def max_hp(self) -> int:
        return self.individual.max_hp()

    def is_fainted(self) -> bool:
        return self.current_hp <= 0

    def apply_damage(self, amount: int) -> int:
        amount = max(0, int(amount))
        if amount <= 0:
            return 0
        self.current_hp = max(0, self.current_hp - amount)
        return amount

    def heal(self, amount: int) -> int:
        amount = max(0, int(amount))
        before = self.current_hp
        self.current_hp = min(self.max_hp(), self.current_hp + amount)
        return self.current_hp - before

    def set_status(self, kind: Optional[str]) -> None:
        if kind is None:
            self.status = None
            self.status_turns = 0
            return
        if kind == "sleep":
            self.status = kind
            self.status_turns = random.randint(1, 3)
        else:
            self.status = kind
            self.status_turns = -1

    def status_text(self) -> str:
        if not self.status:
            return ""
        if self.status == "burn":
            return "BRN"
        if self.status == "paralysis":
            return "PAR"
        if self.status == "poison":
            return "PSN"
        if self.status == "sleep":
            return "SLP"
        return self.status.upper()


@dataclass
class BattleSide:
    participant: BattleParticipant
    team: List[BattlePokemonState]
    active_index: int = 0
    selection_mode: str = "menu"
    queued_action: Optional[QueuedAction] = None

    def active(self) -> BattlePokemonState:
        return self.team[self.active_index]

    def alive_indices(self) -> List[int]:
        return [idx for idx, mon in enumerate(self.team) if not mon.is_fainted()]

    def has_available_switch(self) -> bool:
        return any(idx != self.active_index and not mon.is_fainted() for idx, mon in enumerate(self.team))

    def force_next_available(self) -> bool:
        for idx, mon in enumerate(self.team):
            if idx == self.active_index:
                continue
            if not mon.is_fainted():
                self.active_index = idx
                self.selection_mode = "menu"
                self.queued_action = None
                return True
        return False


@dataclass
class BattleResult:
    participants: Tuple[BattleParticipant, BattleParticipant]
    winner: Optional[int]
    rounds: int
    log: List[str] = field(default_factory=list)
    battle_type: str = "wild"
    rewards: Dict[int, int] = field(default_factory=dict)
    experience_log: Dict[int, List[str]] = field(default_factory=dict)


ACTIVE_SESSIONS: Dict[int, "BattleSession"] = {}


class BattleSession:
    MENU_EMOJIS = {"⚔️": "attack", "🔄": "switch", "🧴": "item", "🏃": "run"}
    NUMBER_EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]

    def __init__(
        self,
        channel: discord.abc.Messageable,
        challenger: BattleParticipant,
        opponent: BattleParticipant,
        battle_type: str = "trainer",
    ) -> None:
        self.channel = channel
        self.participants = (challenger, opponent)
        self.battle_type = battle_type
        self.sides = [
            BattleSide(challenger, [BattlePokemonState(mon) for mon in challenger.party]),
            BattleSide(opponent, [BattlePokemonState(mon) for mon in opponent.party]),
        ]
        self.turn = 1
        self.log: List[str] = []
        self.message: Optional[discord.Message] = None
        self.pending_actions: List[Optional[QueuedAction]] = [None, None]
        self.selection_modes: List[str] = ["menu", "menu"]
        self.item_options: Dict[int, List[str]] = {0: [], 1: []}
        self.experience_log: Dict[int, List[str]] = {}
        self.finished = False
        self.winner: Optional[int] = None
        self.rewards: Dict[int, int] = {}
        self.participation: List[set[int]] = [set(), set()]

    @property
    def challenger(self) -> BattleSide:
        return self.sides[0]

    @property
    def opponent(self) -> BattleSide:
        return self.sides[1]

    async def start(self) -> None:
        for idx, side in enumerate(self.sides):
            if not side.alive_indices():
                raise ValueError("Battle cannot start with empty parties.")
            first_alive = side.alive_indices()[0]
            side.active_index = first_alive
        embed = self._build_live_embed()
        self.message = await self.channel.send(embed=embed)
        ACTIVE_SESSIONS[self.message.id] = self
        await self._register_actions()
        await self._ensure_ai_actions()
        await self._refresh_interface()

    async def _register_actions(self) -> None:
        if not self.message:
            return
        actions: List[Emoji_Action] = []
        for emoji, action in self.MENU_EMOJIS.items():
            actions.append(Emoji_Action(emoji, action, _menu_callback, args=(self, action), pass_user=True))
        for idx, emoji in enumerate(self.NUMBER_EMOJIS):
            actions.append(Emoji_Action(emoji, f"option_{idx+1}", _number_callback, args=(self, idx), pass_user=True))
        await self.message.clear_reactions()
        emoji_actions.active_actions[str(self.message.id)] = []
        await emoji_actions.action_button_list(self.message, actions)

    def _side_index_for_user(self, user_id: int) -> Optional[int]:
        for idx, participant in enumerate(self.participants):
            if participant.user_id == user_id:
                return idx
        return None

    async def on_menu_action(self, action: str, user: discord.User) -> ea_response:
        if self.finished:
            return ea_response(complete_action=False)
        side_index = self._side_index_for_user(user.id)
        if side_index is None:
            return ea_response(complete_action=False)
        side = self.sides[side_index]
        if side.participant.user_id is None:
            return ea_response(complete_action=False)
        if side.selection_mode != "menu":
            await self.channel.send(f"{side.participant.name}, finish your current selection first!", delete_after=10)
            return ea_response(complete_action=False)
        if action == "attack":
            side.selection_mode = "move"
            await self.channel.send(f"{side.participant.name}, choose a move with the number reactions!", delete_after=10)
        elif action == "switch":
            if not side.has_available_switch():
                await self.channel.send(f"{side.participant.name}, there are no healthy Pokémon to switch to.", delete_after=10)
            else:
                side.selection_mode = "switch"
                await self.channel.send(f"{side.participant.name}, pick a party slot to switch in.", delete_after=10)
        elif action == "item":
            options = self._battle_items_for_user(side.participant.user_id)
            if not options:
                await self.channel.send(f"{side.participant.name}, you don't have any usable battle items.", delete_after=10)
            else:
                self.item_options[side_index] = options
                side.selection_mode = "item"
                lines = [f"{idx + 1}. {ITEMS[key]['name']}" for idx, key in enumerate(options)]
                await self.channel.send(f"{side.participant.name}, choose an item:\n" + "\n".join(lines), delete_after=15)
        elif action == "run":
            if self.battle_type == "trainer":
                await self.channel.send("You can't run from a trainer battle!", delete_after=10)
            else:
                self.pending_actions[side_index] = QueuedAction("run", flee=True)
                side.selection_mode = "ready"
                await self._maybe_resolve_turn()
        await self._refresh_interface()
        return ea_response(complete_action=False)

    async def on_number_selection(self, index: int, user: discord.User) -> ea_response:
        if self.finished:
            return ea_response(complete_action=False)
        side_index = self._side_index_for_user(user.id)
        if side_index is None:
            return ea_response(complete_action=False)
        side = self.sides[side_index]
        mode = side.selection_mode
        if mode == "move":
            await self._queue_move(side_index, index)
        elif mode == "switch":
            await self._queue_switch(side_index, index)
        elif mode == "item":
            await self._queue_item(side_index, index)
        else:
            return ea_response(complete_action=False)
        await self._refresh_interface()
        return ea_response(complete_action=False)

    async def _queue_move(self, side_index: int, index: int) -> None:
        side = self.sides[side_index]
        moveset = side.active().individual.get_move_objects()
        if index >= len(moveset):
            await self.channel.send(f"{side.participant.name}, that move slot is empty.", delete_after=10)
            return
        move = moveset[index]
        side.selection_mode = "ready"
        side.queued_action = QueuedAction("move", move=move)
        self.pending_actions[side_index] = side.queued_action
        side.active().participated = True
        self.participation[side_index].add(side.active_index)
        await self.channel.send(f"{side.participant.name} queued {move.name}!", delete_after=8)
        await self._maybe_resolve_turn()

    async def _queue_switch(self, side_index: int, index: int) -> None:
        side = self.sides[side_index]
        slot = index
        if slot < 0 or slot >= len(side.team):
            await self.channel.send("That party slot doesn't exist yet.", delete_after=10)
            return
        if side.team[slot].is_fainted():
            await self.channel.send("That Pokémon has fainted and can't battle.", delete_after=10)
            return
        if slot == side.active_index:
            await self.channel.send("They're already in battle!", delete_after=10)
            return
        side.selection_mode = "ready"
        action = QueuedAction("switch", switch_index=slot)
        side.queued_action = action
        self.pending_actions[side_index] = action
        await self.channel.send(f"{side.participant.name} will switch to slot {slot + 1}.", delete_after=8)
        await self._maybe_resolve_turn()

    async def _queue_item(self, side_index: int, index: int) -> None:
        options = self.item_options.get(side_index) or []
        if index >= len(options):
            await self.channel.send("That item option isn't available.", delete_after=10)
            return
        item_key = options[index]
        side = self.sides[side_index]
        action = QueuedAction("item", item_key=item_key)
        side.selection_mode = "ready"
        side.queued_action = action
        self.pending_actions[side_index] = action
        try:
            item_record = ITEMS[item_key]
        except FileNotFoundError:
            item_record = {"name": item_key.title()}
        item_name = item_record.get("name", item_key.title())
        await self.channel.send(f"{side.participant.name} readies a {item_name}!", delete_after=8)
        await self._maybe_resolve_turn()

    async def _ensure_ai_actions(self) -> None:
        for idx, side in enumerate(self.sides):
            if side.participant.user_id is not None:
                continue
            if self.pending_actions[idx] is None and not self.finished:
                await self._queue_ai_action(idx)

    async def _queue_ai_action(self, side_index: int) -> None:
        side = self.sides[side_index]
        attacker = side.active()
        moveset = attacker.individual.get_move_objects()
        move = None
        if moveset:
            move = max(moveset, key=lambda m: m.power)
        if not move:
            move = moves.get("tackle")
        action = QueuedAction("move", move=move)
        side.queued_action = action
        self.pending_actions[side_index] = action
        attacker.participated = True
        self.participation[side_index].add(side.active_index)

    async def _maybe_resolve_turn(self) -> None:
        await self._ensure_ai_actions()
        if all(action is not None for action in self.pending_actions):
            await self._resolve_turn()

    async def _resolve_turn(self) -> None:
        if self.finished:
            return
        actions: List[Tuple[int, QueuedAction]] = []
        for idx, action in enumerate(self.pending_actions):
            if action is not None:
                actions.append((idx, action))
        order = sorted(actions, key=lambda entry: self._action_order_key(*entry), reverse=True)
        turn_log: List[str] = []
        for side_index, action in order:
            if self.finished:
                break
            side = self.sides[side_index]
            if action.kind == "move":
                entry = self._execute_move(side_index, action.move)
                if entry:
                    turn_log.append(entry)
            elif action.kind == "switch":
                entry = self._execute_switch(side_index, action.switch_index)
                if entry:
                    turn_log.append(entry)
            elif action.kind == "item":
                entry = self._execute_item(side_index, action.item_key)
                if entry:
                    turn_log.append(entry)
            elif action.kind == "run":
                self.finished = True
                self.winner = 1 - side_index
                turn_log.append(f"{self.sides[side_index].participant.name} fled the battle!")
        self.turn += 1
        for idx in range(len(self.sides)):
            if self.finished:
                break
            status_entry = self._apply_end_of_turn_status(idx)
            if status_entry:
                turn_log.append(status_entry)
        self.pending_actions = [None, None]
        for side in self.sides:
            if side.selection_mode != "switch":
                side.selection_mode = "menu"
            side.queued_action = None
        self.log.extend(turn_log)
        if self.finished:
            await self._conclude_battle()
        else:
            await self._refresh_interface(extra_log=turn_log)

    def _action_order_key(self, side_index: int, action: QueuedAction) -> Tuple[int, int, float]:
        if action.kind == "run":
            priority = 6
        elif action.kind == "switch":
            priority = 5
        elif action.kind == "item":
            priority = 4
        elif action.kind == "move" and action.move:
            priority = 3 + action.move.priority
        else:
            priority = 0
        speed = self.sides[side_index].active().individual.get_stats()["speed"]
        return (priority, speed, random.random())

    def _execute_move(self, side_index: int, move: Optional[moves.Move]) -> Optional[str]:
        side = self.sides[side_index]
        attacker = side.active()
        if attacker.is_fainted():
            return None
        if attacker.status == "sleep":
            if attacker.status_turns > 0:
                attacker.status_turns -= 1
                if attacker.status_turns <= 0:
                    attacker.set_status(None)
                    return f"{attacker.individual.get_title()} woke up!"
                return f"{attacker.individual.get_title()} is fast asleep!"
        if attacker.status == "paralysis" and random.random() < 0.25:
            return f"{attacker.individual.get_title()} is paralyzed! It can't move!"
        if not move:
            move = moves.get("tackle")
        target_index = 1 - side_index
        defender_side = self.sides[target_index]
        defender = defender_side.active()
        damage = self._calculate_damage(attacker, defender, move)
        healed = 0
        if damage > 0:
            defender.apply_damage(damage)
        if move.heal:
            healed = attacker.heal(move.heal)
        entry = f"{attacker.individual.get_title()} used {move.name}!"
        if damage:
            entry += f" It dealt {damage} damage."
        if healed:
            entry += f" It restored {healed} HP!"
        if move.status and not defender.is_fainted():
            if random.random() <= move.status_chance:
                if defender.status != move.status:
                    defender.set_status(move.status)
                    entry += f" {defender.individual.get_title()} is now {defender.status_text()}!"
        if defender.is_fainted():
            entry += f" {defender.individual.get_title()} fainted!"
            faint_message = self._handle_faint(target_index)
            if faint_message:
                entry += f" {faint_message}"
        return entry

    def _execute_switch(self, side_index: int, slot: Optional[int]) -> Optional[str]:
        if slot is None:
            return None
        side = self.sides[side_index]
        if slot < 0 or slot >= len(side.team):
            return None
        side.active_index = slot
        side.selection_mode = "menu"
        return f"{side.participant.name} sent out {side.active().individual.get_title()}!"

    def _execute_item(self, side_index: int, item_key: Optional[str]) -> Optional[str]:
        if not item_key:
            return None
        side = self.sides[side_index]
        uid = side.participant.user_id
        if uid is None:
            return None
        try:
            item_data = ITEMS[item_key]
        except FileNotFoundError:
            return f"{side.participant.name} tried to use an unknown item."
        if not economy.user_spend_item(uid, item_key, 1):
            return f"{side.participant.name} tried to use a {item_data['name']}, but didn't have one!"
        item = item_data
        heal_amount = int(item.get("battle_heal", 0))
        healed = side.active().heal(heal_amount)
        return f"{side.participant.name} used {item['name']} and restored {healed} HP!"

    def _calculate_damage(self, attacker: BattlePokemonState, defender: BattlePokemonState, move: moves.Move) -> int:
        if move.category == "status" or move.power <= 0:
            return 0
        atk_stats = attacker.individual.get_stats()
        def_stats = defender.individual.get_stats()
        if move.category == "physical":
            attack_stat = atk_stats["attack"]
            if attacker.status == "burn":
                attack_stat = max(1, int(attack_stat * 0.8))
            defense_stat = def_stats["defense"]
        else:
            attack_stat = atk_stats["sp_attack"]
            defense_stat = def_stats["sp_defense"]
        level = attacker.individual.level
        base = (((2 * level / 5) + 2) * move.power * attack_stat / max(1, defense_stat)) / 50 + 2
        modifier = random.uniform(0.85, 1.0)
        stab = 1.0
        attacker_types = [attacker.individual.species.type_1.name]
        if attacker.individual.species.type_2:
            attacker_types.append(attacker.individual.species.type_2.name)
        if move.type in attacker_types:
            stab = 1.5
        damage = int(base * modifier * stab)
        return max(1, damage)

    def _handle_faint(self, side_index: int) -> Optional[str]:
        side = self.sides[side_index]
        if side.participant.user_id is None:
            if side.force_next_available():
                self.pending_actions[side_index] = None
                side.selection_mode = "menu"
                return None
        else:
            if side.has_available_switch():
                self.pending_actions[side_index] = None
                side.selection_mode = "switch"
                return f"{side.participant.name}, choose your next Pokémon!"
        self.finished = True
        self.winner = 1 - side_index
        return None

    def _apply_end_of_turn_status(self, side_index: int) -> Optional[str]:
        side = self.sides[side_index]
        active = side.active()
        if active.is_fainted() or not active.status:
            return None
        if active.status == "burn":
            damage = max(1, active.max_hp() // 16)
            active.apply_damage(damage)
            message = f"{active.individual.get_title()} is hurt by its burn! (-{damage} HP)"
            if active.is_fainted():
                faint_message = self._handle_faint(side_index)
                if faint_message:
                    message += f" {faint_message}"
            return message
        if active.status == "poison":
            damage = max(1, active.max_hp() // 8)
            active.apply_damage(damage)
            message = f"{active.individual.get_title()} is hurt by poison! (-{damage} HP)"
            if active.is_fainted():
                faint_message = self._handle_faint(side_index)
                if faint_message:
                    message += f" {faint_message}"
            return message
        return None

    async def _conclude_battle(self) -> None:
        await self._distribute_rewards_and_xp()
        self._record_battles()
        result = BattleResult(
            participants=self.participants,
            winner=self.winner,
            rounds=self.turn,
            log=self.log,
            battle_type=self.battle_type,
            rewards=self.rewards,
            experience_log=self.experience_log,
        )
        if self.message:
            await self.message.clear_reactions()
            await self.message.edit(embed=embeds.battle(result))
            ACTIVE_SESSIONS.pop(self.message.id, None)

    async def _distribute_rewards_and_xp(self) -> None:
        challenger, opponent = self.sides
        if self.battle_type == "trainer":
            if self.winner is None:
                rewards = {challenger.participant.user_id: 2, opponent.participant.user_id: 2}
            elif self.winner == 0:
                rewards = {challenger.participant.user_id: 5, opponent.participant.user_id: 1}
            else:
                rewards = {challenger.participant.user_id: 1, opponent.participant.user_id: 5}
        else:
            rewards = {}
            if self.winner == 0:
                rewards[challenger.participant.user_id] = 3
            elif self.winner == 1:
                rewards[opponent.participant.user_id] = 3
        for uid, amount in rewards.items():
            if uid is None or amount <= 0:
                continue
            users.adjust_bp(uid, amount)
        self.rewards = {uid: amount for uid, amount in rewards.items() if uid is not None}
        await self._award_experience()

    def _record_battles(self) -> None:
        challenger, opponent = self.participants
        if challenger.user_id:
            if self.winner is None:
                outcome = "draw"
            elif self.winner == 0:
                outcome = "win"
            else:
                outcome = "loss"
            context = {"type": self.battle_type}
            if self.battle_type == "trainer" and opponent.user_id:
                context["opponent"] = opponent.user_id
            elif self.battle_type == "wild" and opponent.party:
                wild = opponent.party[0]
                context.update({"pokemon": wild.species.pokedex_number, "name": wild.species.name})
            users.record_battle(challenger.user_id, outcome, context)
        if opponent.user_id:
            if self.winner is None:
                outcome = "draw"
            elif self.winner == 1:
                outcome = "win"
            else:
                outcome = "loss"
            context = {"type": self.battle_type}
            if self.battle_type == "trainer" and challenger.user_id:
                context["opponent"] = challenger.user_id
            elif self.battle_type == "wild" and challenger.party:
                wild = challenger.party[0]
                context.update({"pokemon": wild.species.pokedex_number, "name": wild.species.name})
            users.record_battle(opponent.user_id, outcome, context)

    async def _award_experience(self) -> None:
        self.experience_log = {}
        for idx, side in enumerate(self.sides):
            participant = side.participant
            if participant.user_id is None:
                continue
            events: List[str] = []
            xp_gain = self._xp_for_side(idx)
            if xp_gain <= 0:
                continue
            user_record = users.ensure_user_record(participant.user_id)
            roster = user_record.get("pokemon", [])
            roster_map = {entry.get("uid"): pos for pos, entry in enumerate(roster)}
            for mon in side.team:
                if not mon.participated:
                    continue
                uid = mon.individual.instance_id
                pos = roster_map.get(uid, -1)
                mon_events = mon.individual.gain_experience(xp_gain)
                if pos >= 0:
                    roster[pos] = mon.individual.to_dict()
                if mon_events["level"] or mon_events["evolution"]:
                    events.extend([f"{mon.individual.get_title()}: {msg}" for msg in mon_events["level"] + mon_events["evolution"]])
            user_record["pokemon"] = roster
            users.USERS[participant.user_id] = user_record
            users.USERS.save_item(participant.user_id)
            if events:
                self.experience_log[participant.user_id] = events

    def _xp_for_side(self, side_index: int) -> int:
        opponent_index = 1 - side_index
        defeated_levels = []
        for mon in self.sides[opponent_index].team:
            if mon.is_fainted():
                defeated_levels.append(mon.individual.level)
        if not defeated_levels:
            return 0
        base = sum(level for level in defeated_levels) // max(1, len(defeated_levels))
        return max(10, base * 5)

    def _battle_items_for_user(self, user_id: Optional[int]) -> List[str]:
        if user_id is None:
            return []
        usable = []
        for key in ("potion", "superpotion"):
            try:
                count = economy.user_item_count(user_id, key)
            except Exception:
                count = 0
            if count > 0:
                usable.append(key)
        return usable

    def _build_live_embed(self, extra_log: Optional[Iterable[str]] = None) -> discord.Embed:
        title = "Trainer Battle" if self.battle_type == "trainer" else "Wild Encounter"
        embed = discord.Embed(title=title, color=0x5B6EE1 if self.battle_type == "trainer" else 0xE12005)
        embed.description = f"Turn {self.turn}\nReact with the emojis to choose your action."
        for idx, side in enumerate(self.sides):
            active = side.active()
            hp_line = f"HP: {active.current_hp}/{active.max_hp()}"
            status = active.status_text()
            status_text = f" [{status}]" if status else ""
            moveset = ", ".join(move.name for move in active.individual.get_move_objects())
            embed.add_field(
                name=f"{self.participants[idx].name}",
                value=(
                    f"{active.individual.get_title()} Lv{active.individual.level}{status_text}\n"
                    f"{hp_line}\n"
                    f"Moves: {moveset if moveset else '—'}"
                ),
                inline=False,
            )
        history = list(extra_log or [])
        if not history and self.log:
            history = self.log[-5:]
        if history:
            embed.add_field(name="Recent Events", value="\n".join(history[-5:]), inline=False)
        return embed

    async def _refresh_interface(self, extra_log: Optional[Iterable[str]] = None) -> None:
        if not self.message or self.finished:
            return
        embed = self._build_live_embed(extra_log)
        await self.message.edit(embed=embed)


async def start_trainer_battle(
    message: discord.Message,
    challenger_id: int,
    challenger_name: str,
    challenger_party: Sequence[classes.Individual],
    opponent_id: int,
    opponent_name: str,
    opponent_party: Sequence[classes.Individual],
) -> None:
    challenger = BattleParticipant(challenger_id, challenger_name, challenger_party)
    opponent = BattleParticipant(opponent_id, opponent_name, opponent_party)
    session = BattleSession(message.channel, challenger, opponent, "trainer")
    await session.start()


async def start_wild_battle(
    channel: discord.abc.Messageable,
    trainer_id: int,
    trainer_name: str,
    party: Sequence[classes.Individual],
    wild: classes.Individual,
) -> None:
    challenger = BattleParticipant(trainer_id, trainer_name, party)
    opponent = BattleParticipant(None, f"Wild {wild.species.name}", [wild])
    session = BattleSession(channel, challenger, opponent, "wild")
    await session.start()


async def handle_reaction(message_id: int, emoji: str, user: discord.User) -> Optional[ea_response]:
    session = ACTIVE_SESSIONS.get(message_id)
    if not session:
        return None
    if emoji in BattleSession.MENU_EMOJIS:
        return await session.on_menu_action(BattleSession.MENU_EMOJIS[emoji], user)
    if emoji in BattleSession.NUMBER_EMOJIS:
        index = BattleSession.NUMBER_EMOJIS.index(emoji)
        return await session.on_number_selection(index, user)
    return None


async def _menu_callback(payload) -> ea_response:
    (session, action), user = payload
    return await session.on_menu_action(action, user)


async def _number_callback(payload) -> ea_response:
    (session, index), user = payload
    return await session.on_number_selection(index, user)
