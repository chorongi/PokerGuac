import numpy as np
import time

from typing import List, Dict, Any, Optional, Tuple, cast

from .components.constants import (
    POKER_CARD_DECK,
    NUM_PLAYERS_TO_POSITIONS,
    ALL_POKER_STAGES,
    MIN_NUM_PLAYERS,
    MAX_NUM_PLAYERS,
    BOARD_NUM_CARDS,
    HOLDEM_NUM_PLAYER_CARDS,
    NUM_FLOP_CARDS,
    NUM_TURN_CARDS,
    NUM_RIVER_CARDS,
    PokerStage,
    PokerTableState,
)
from .components.card import PokerCard, PokerBoard, PokerHole
from .poker_player import PokerPlayer, PlayerAction, PlayerStatus
from .components.rules import rank_hands
from ..config import TableGameConfig, PokerGameType


CARD_DECK_SIZE = 52


class PokerTable:
    board: PokerBoard
    cards: List[PokerCard]
    active_card_deck: List[PokerCard]
    players: List[Optional[PokerPlayer]]
    eliminated_players: Dict[PokerPlayer, int]
    per_player_action: Dict[PokerStage, List[List[Tuple[PlayerAction, float]]]]
    num_hand_players: int
    num_alive_hand_players: int
    num_player_cards: int
    button: Optional[int]
    active: bool
    stage: PokerStage
    state: PokerTableState
    hand_number: int
    cfg: TableGameConfig

    def __init__(
        self,
        num_players: int,
        big_blind: float,
        small_blind: float,
        min_buy_in: float,
        max_buy_in: float,
        num_player_cards: int = HOLDEM_NUM_PLAYER_CARDS,
        game_type: PokerGameType = PokerGameType.HOLDEM,
    ):
        assert num_players >= MIN_NUM_PLAYERS and num_players <= MAX_NUM_PLAYERS
        self.num_players = num_players
        self.num_player_cards = num_player_cards
        self.active = False
        self.cfg = TableGameConfig(
            big_blind=big_blind,
            small_blind=small_blind,
            min_buy_in=min_buy_in,
            max_buy_in=max_buy_in,
            game_type=game_type,
        )
        self.reset()

    def reset(self):
        self.hand_number = 0
        self.num_hand_players = 0
        self.num_alive_hand_players = 0
        self.board = [None] * BOARD_NUM_CARDS
        self.players = [None for _ in range(self.num_players)]
        self.button = None
        self.eliminated_players = {}
        self.cards = []
        self.per_player_action = {
            stage: [[] for _ in range(self.num_players)] for stage in ALL_POKER_STAGES
        }

    def activate_table(self):
        assert self.get_num_hand_players() >= MIN_NUM_PLAYERS
        self.cards = [
            PokerCard(card_str[0], card_str[1]) for card_str in POKER_CARD_DECK
        ]
        assert len(self.cards) == CARD_DECK_SIZE
        self.active_card_deck = self.cards.copy()
        if self.button is None:
            self.init_button()
        self.round_reset()
        self.active = True

    def break_table(self) -> List[PokerPlayer]:
        remaining_players = []
        for player in self.players:
            if player is not None:
                remaining_players.append(player)
        self.reset()
        self.active = False
        return remaining_players

    def init_button(self):
        # init button
        playing_indices = []
        for i, player in enumerate(self.players):
            if player is not None and player.is_joining():
                playing_indices.append(i)
        self.button = np.random.choice(playing_indices)

    def move_button(self):
        # move button
        assert self.button is not None
        self.button = (self.button + 1) % self.num_players
        button_player = self.players[self.button]
        while button_player is None or not button_player.is_joining():
            self.button = (self.button + 1) % self.num_players
            button_player = self.players[self.button]

    def _assign_positions(self):
        # Assign positions for active players
        assert self.button is not None
        button_idx = self.button
        self.num_hand_players = self.get_num_hand_players()
        self.num_alive_hand_players = self.num_hand_players
        assert self.num_hand_players >= MIN_NUM_PLAYERS
        # TODO (hkwark): Need to wait for sitting out players to come back to start the game
        player_positions = NUM_PLAYERS_TO_POSITIONS[self.num_hand_players]
        count = 0
        for i in range(1, self.num_players + 1):
            idx = (button_idx + i) % self.num_players
            player = self.players[idx]
            if player is not None and player.is_joining():
                player.position = player_positions[count]
                player.status = PlayerStatus.WAITING_TURN
                count += 1
        assert count == len(player_positions)

    def _next(self):
        assert self.player_in_action is not None
        self.player_in_action = (self.player_in_action + 1) % self.num_players
        curr_player = self.players[self.player_in_action]
        counter = 1
        while curr_player is None or not curr_player.is_active():
            self.player_in_action = (self.player_in_action + 1) % self.num_players
            curr_player = self.players[self.player_in_action]
            counter += 1
            if counter >= self.num_players:
                # There might not be a next person to act if everyone all-ins
                break

    def round_reset(self):
        for player in self.players:
            if player is None:
                continue
            player.hand_reset()
        self.per_player_action = {
            stage: [[] for _ in range(self.num_players)] for stage in ALL_POKER_STAGES
        }
        self.stage = PokerStage.PREFLOP
        self.state = PokerTableState.BLIND
        self.player_in_action = self.button
        self._next()
        self._assign_positions()

    def _blind(self):
        assert self.player_in_action is not None
        small_blind = self.players[self.player_in_action]
        assert small_blind is not None
        bet = small_blind.blind(self.cfg["small_blind"], self.cfg["big_blind"])
        self.per_player_action[self.stage][self.player_in_action].append(
            (PlayerAction.SMALL_BLIND, bet)
        )
        self._next()

        big_blind = self.players[self.player_in_action]
        assert big_blind is not None
        bet = big_blind.blind(self.cfg["big_blind"], self.cfg["big_blind"])
        self.per_player_action[self.stage][self.player_in_action].append(
            (PlayerAction.BIG_BLIND, bet)
        )
        if big_blind.status == PlayerStatus.RAISE and not small_blind.is_all_in():
            small_blind.status = PlayerStatus.WAITING_TURN
        self._next()

    def get_player_stacks(self):
        stacks = []
        for i in range(self.num_players):
            player = self.players[i]
            if player is None:
                stacks.append(0.0)
            else:
                stacks.append(player.stack)
        return stacks

    def _straddle(self):
        assert self.player_in_action is not None
        straddle_player = self.players[self.player_in_action]
        assert straddle_player is not None
        if straddle_player.straddle(
            self.get_player_stacks(), self.player_in_action, self.cfg["big_blind"]
        ):
            self.per_player_action[self.stage][self.player_in_action].append(
                (PlayerAction.STRADDLE, 2 * self.cfg["big_blind"])
            )
            for player in self.players:
                if (
                    player is None
                    or player == straddle_player
                    or not player.is_active()
                ):
                    continue
                else:
                    player.status = PlayerStatus.WAITING_TURN
            self._next()

    def _shuffle(self):
        assert len(self.cards) == CARD_DECK_SIZE
        np.random.shuffle(self.cards)  # type: ignore
        self.active_card_deck = self.cards.copy()

    def _deal(self):
        assert self.button is not None
        hands: List[List[PokerCard]] = [[] for _ in range(self.num_player_cards)]
        for i in range(self.num_player_cards):
            for _ in range(self.num_hand_players):
                hands[i].append(self.active_card_deck.pop())

        count = 0
        for player_idx in range(self.button + 1, self.button + self.num_players + 1):
            player = self.players[player_idx % self.num_players]
            if player is not None and player.is_joining():
                player.set_card(
                    cast(
                        PokerHole,
                        tuple([hands[i][count] for i in range(self.num_player_cards)]),
                    )
                )
                count += 1

    def _round_finished(self) -> bool:
        return self.get_num_alive_players() < MIN_NUM_PLAYERS

    def _action_finished(self) -> bool:
        action_finished = True
        raise_counter = 0
        for player in self.players:
            if player is None:
                continue
            elif player.status == PlayerStatus.WAITING_TURN:
                action_finished = False
            elif player.status == PlayerAction.RAISE and not player.is_all_in():
                raise_counter += 1

        if raise_counter >= MIN_NUM_PLAYERS:
            action_finished = False

        return action_finished

    def player_action(self, curr_player: PokerPlayer):
        assert self.player_in_action is not None
        bet, action = curr_player.action(
            self.board,
            self.per_player_action,
            self.get_player_stacks(),
            self.player_in_action,
            self.cfg["big_blind"],
        )
        self.per_player_action[self.stage][self.player_in_action].append((action, bet))
        if action == PlayerAction.RAISE:
            for player in self.players:
                if player is None or player == curr_player or not player.is_active():
                    continue
                else:
                    player.status = PlayerStatus.WAITING_TURN
        self._next()

    def _action(self):
        assert self.player_in_action is not None
        while not self._action_finished():
            curr_player = self.players[self.player_in_action]
            assert curr_player is not None
            assert curr_player.stack > 0, curr_player.stack
            self.player_action(curr_player)

    def _end_stage(self):
        # Done with all betting actions. Prepare for next stage
        for player in self.players:
            if player is not None:
                player.stage_reset(self.stage)
            else:
                continue
        self.stage = self.stage.next()

    def _eliminate_players(self):
        for i, player in enumerate(self.players):
            if player is None:
                continue
            else:
                assert player.stack >= 0, (player.name, player.stack)
                if np.isclose(player.stack, 0):
                    player.try_buy_in(self.cfg["min_buy_in"], self.cfg["max_buy_in"])
                    if player.is_eliminated() and player not in self.eliminated_players:
                        # Eliminate Player
                        self.eliminated_players[player] = self.hand_number
                        self.players[i] = None

    def get_num_living_players(self) -> int:
        """
        Get number of players surviving in the game. (Not Eliminated)
        """
        num_out_players = 0
        for player in self.players:
            if player is None or player.is_eliminated():
                num_out_players += 1
        num_alive_players = self.num_players - num_out_players
        return num_alive_players

    def get_num_active_players(self) -> int:
        """
        get number of players that can take action (Bet)
        """
        num_active_players = 0
        for player in self.players:
            if player is not None and player.is_active():
                num_active_players += 1
        return num_active_players

    def get_num_alive_players(self) -> int:
        """
        get number of players participating in current hand (but can be all-in)
        """
        num_alive_players = 0
        for player in self.players:
            if player is not None and player.is_alive():
                num_alive_players += 1
        return num_alive_players

    def get_num_hand_players(self) -> int:
        """
        get number of players that can receive a new hand.
        """
        num_hand_players = 0
        for player in self.players:
            if player is not None and player.is_joining():
                num_hand_players += 1
        return num_hand_players

    def get_living_players(self) -> List[PokerPlayer]:
        """
        get number of players surviving. (Not eliminated)
        """
        living_players = []
        for player in self.players:
            if player is not None and not player.is_eliminated():
                living_players.append(player)
        return living_players

    def get_per_player_bets(self) -> List[float]:
        """
        get per player total bet in current stage (for display)
        """
        stage_actions = self.per_player_action[self.stage]
        assert len(stage_actions) == self.num_players
        player_bets = []
        for i in range(self.num_players):
            total_bet = 0
            for action, bet in stage_actions[i]:
                total_bet += bet
            player_bets.append(total_bet)
        return player_bets

    def get_num_empty_seats(self) -> int:
        count = 0
        for player in self.players:
            if player is None:
                count += 1
        return count

    def preflop(self):
        assert self.get_num_active_players() >= MIN_NUM_PLAYERS
        assert self.get_num_active_players() == self.num_hand_players
        assert self.stage == PokerStage.PREFLOP
        self._blind()
        self._straddle()
        self._shuffle()
        self._deal()
        self._action()
        self._end_stage()

    def flop(self):
        if self._round_finished():
            self._end_stage()
        else:
            assert (
                len(self.active_card_deck)
                == CARD_DECK_SIZE - self.num_player_cards * self.num_hand_players
            )
            assert self.stage == PokerStage.FLOP
            self.active_card_deck.pop()
            for i in range(NUM_FLOP_CARDS):
                self.board[i] = self.active_card_deck.pop()
            self._action()
            self._end_stage()

    def turn(self):
        if self._round_finished():
            return
        else:
            assert (
                len(self.active_card_deck)
                == CARD_DECK_SIZE
                - self.num_player_cards * self.num_hand_players
                - NUM_FLOP_CARDS
                - 1
            )
            assert self.stage == PokerStage.TURN
            self.active_card_deck.pop()
            for i in range(NUM_TURN_CARDS):
                self.board[NUM_FLOP_CARDS + i] = self.active_card_deck.pop()
            self._action()
            self._end_stage()

    def river(self):
        if self._round_finished():
            return
        else:
            assert (
                len(self.active_card_deck)
                == CARD_DECK_SIZE
                - self.num_player_cards * self.num_hand_players
                - NUM_FLOP_CARDS
                - NUM_TURN_CARDS
                - 2
            )
            assert self.stage == PokerStage.RIVER
            self.active_card_deck.pop()
            for i in range(NUM_RIVER_CARDS):
                self.board[
                    NUM_FLOP_CARDS + NUM_TURN_CARDS + i
                ] = self.active_card_deck.pop()
            self._action()
            self._end_stage()

    def end_round(self):
        self._cashing()
        self._eliminate_players()

    def _cashing(self):
        player_holes = []
        candidate_players = []
        pre_cash_stack = self.get_table_stack_size()
        pot_size = self.get_pot_size()
        for player in self.players:
            if player is None:
                continue
            elif player.status in [
                PlayerStatus.CALL,
                PlayerStatus.RAISE,
            ]:
                player_holes.append(player.open_cards())
                candidate_players.append(player)

        player_ranks, _ = rank_hands(self.board, player_holes)
        ranked_players = {}
        for rank, player in zip(player_ranks, candidate_players):
            if rank in ranked_players:
                ranked_players[rank].append(self.players.index(player))
            else:
                ranked_players[rank] = [self.players.index(player)]

        total_pot = self.get_pot_size()
        per_player_bet = PokerPlayer.per_player_action_to_bet(self.per_player_action)
        for rank in sorted(ranked_players.keys()):
            if np.allclose(total_pot, 0):
                break
            elif total_pot < 0:
                raise ValueError(
                    f"Something has gone wrong with cashing out! Total pot size {total_pot} is different from total prize"
                )
            else:
                num_ties = len(ranked_players[rank])
                players = [self.players[i] for i in ranked_players[rank]]
                bets = np.array([per_player_bet[i] for i in ranked_players[rank]])
                players_and_bets = sorted(zip(players, bets), key=lambda x: x[1])
                players, bets = [x[0] for x in players_and_bets], [
                    x[1] for x in players_and_bets
                ]
                bets = np.array([0] + bets)
                bets = bets[1:] - bets[:-1]
                rank_cashed_outs = np.zeros(self.num_players)
                per_player_bets = per_player_bet
                for i, player in enumerate(players):
                    cashed_out_bets = np.zeros(self.num_players)
                    for j in range(i + 1):
                        player_pots = np.minimum(bets[j], per_player_bets)
                        cashed_out_bets += player_pots / num_ties
                        per_player_bets = per_player_bets - player_pots / num_ties

                    if np.allclose(cashed_out_bets, 0):
                        # Added for floating point precision errors
                        cashed_out_bets = np.zeros(self.num_players)
                    rank_cashed_outs += cashed_out_bets
                    player.cash(np.sum(cashed_out_bets))
                    total_pot = total_pot - np.sum(cashed_out_bets)
                    num_ties = num_ties - 1

                per_player_bet = per_player_bet - rank_cashed_outs

        assert np.allclose(total_pot, 0), total_pot
        assert np.allclose(per_player_bet, np.zeros(self.num_players)), (
            per_player_bet,
            np.zeros(self.num_players),
        )
        assert np.allclose(pre_cash_stack + pot_size, self.get_table_stack_size()), (
            pre_cash_stack,
            pot_size,
            self.get_table_stack_size(),
        )
        self.per_player_action = {
            stage: [[] for _ in range(self.num_players)] for stage in ALL_POKER_STAGES
        }

    def play_hand(self):
        """
        simulate a single hand round (preflop, flop, turn, river)
        """
        assert self.active
        assert self.get_num_hand_players() >= MIN_NUM_PLAYERS, self.players
        self.hand_number += 1
        self.round_reset()
        self.preflop()
        self.flop()
        self.turn()
        self.river()
        self.end_round()
        self.move_button()

    def step(self):
        """
        Function used to do a step-by-step progression of a poker game.
        Use this for playing interactive poker with step-by-step actions.
        """
        assert self.active
        print(self.state)
        match self.state:
            case PokerTableState.BLIND:
                self._blind()
                self.state = PokerTableState.STRADDLE
            case PokerTableState.STRADDLE:
                self._straddle()
                self.state = PokerTableState.DRAW_CARDS
            case PokerTableState.DRAW_CARDS:
                match self.stage:
                    case PokerStage.PREFLOP:
                        self._shuffle()
                        self._deal()
                    case PokerStage.FLOP:
                        self.active_card_deck.pop()
                        for i in range(NUM_FLOP_CARDS):
                            self.board[i] = self.active_card_deck.pop()
                    case PokerStage.TURN:
                        self.active_card_deck.pop()
                        for i in range(NUM_TURN_CARDS):
                            self.board[NUM_FLOP_CARDS + i] = self.active_card_deck.pop()
                    case PokerStage.RIVER:
                        self.active_card_deck.pop()
                        for i in range(NUM_RIVER_CARDS):
                            self.board[
                                NUM_FLOP_CARDS + NUM_TURN_CARDS + i
                            ] = self.active_card_deck.pop()
                if self._action_finished():
                    self.state = PokerTableState.END_STAGE
                else:
                    self.state = PokerTableState.PLAYER_ACTION
            case PokerTableState.PLAYER_ACTION:
                if not self._action_finished():
                    assert self.player_in_action is not None
                    curr_player = self.players[self.player_in_action]
                    assert curr_player is not None
                    assert curr_player.stack > 0, curr_player.stack
                    self.player_action(curr_player)
                if self._action_finished():
                    # all players have finished taking action
                    self.state = PokerTableState.END_STAGE
            case PokerTableState.END_STAGE:
                if self.stage == PokerStage.RIVER:
                    self._end_stage()
                    self.state = PokerTableState.END_ROUND
                else:
                    self._end_stage()
                    self.state = PokerTableState.DRAW_CARDS
            case PokerTableState.END_ROUND:
                self.end_round()
                if self.get_num_hand_players() < MIN_NUM_PLAYERS:
                    self.state = PokerTableState.PAUSED
                else:
                    self.state = PokerTableState.MOVE_BUTTON
            case PokerTableState.MOVE_BUTTON:
                self.move_button()
                self.state = PokerTableState.BLIND

    def get_pot_size(self) -> float:
        return np.sum(PokerPlayer.per_player_action_to_bet(self.per_player_action))

    def get_table_stack_size(self) -> float:
        stack = 0
        for player in self.players:
            if player is not None:
                stack += player.stack
        return stack

    def seat_player(self, new_player: PokerPlayer) -> bool:
        empty_seats = []
        if new_player.is_eliminated():
            success = False
        else:
            for i, player in enumerate(self.players):
                if player is None:
                    empty_seats.append(i)
            success = len(empty_seats) > 0
            if success:
                seat = np.random.choice(empty_seats)
                self.players[seat] = new_player
        return success

    def update_blind(self, small_blind: float, big_blind: float):
        self.cfg["small_blind"] = small_blind
        self.cfg["big_blind"] = big_blind

    def player_has_holes(self) -> bool:
        for player in self.players:
            if player is not None:
                hole = player.hole
                if hole is not None:
                    return True
        return False

    def can_activate(self):
        return (not self.active) and self.get_num_hand_players() >= MIN_NUM_PLAYERS

    def paused(self):
        return (
            self.active
            and self.get_num_hand_players() < MIN_NUM_PLAYERS
            and self.stage == PokerStage.PREFLOP
            and not self.player_has_holes()
        )

    def finished(self):
        return self.get_num_living_players() < MIN_NUM_PLAYERS

    def player_rankings(self) -> List[PokerPlayer]:
        num_alive = self.get_num_living_players()
        # sort by remaining stack if not eliminated
        live_players = self.get_living_players()

        assert len(live_players) == num_alive
        player_rankings = sorted(
            self.eliminated_players.keys(),
            key=lambda x: self.eliminated_players[x],
        ) + sorted(live_players, key=lambda x: x.stack)
        player_rankings.reverse()
        return player_rankings

    def player_rankings_report(self) -> Tuple[Dict[PokerPlayer, Dict[str, Any]], str]:
        report = {}
        for player in self.eliminated_players:
            report[player] = {}
            report[player]["name"] = player.name
            report[player]["stack"] = player.stack
            assert np.isclose(player.stack, 0)
            report[player]["num_hands_played"] = self.eliminated_players[player]

        for player in self.get_living_players():
            assert player not in self.eliminated_players
            report[player] = {}
            report[player]["name"] = player.name
            report[player]["stack"] = player.stack
            report[player]["num_hands_played"] = self.hand_number

        report_str = ""
        for i, player in enumerate(self.player_rankings(), 1):
            report_str += f"{i}. {report[player]}\n"
        return report, report_str
