import numpy as np

from typing import List, Dict, Any, Optional, Tuple

from .components.constants import (
    POKER_CARD_DECK,
    NUM_PLAYERS_TO_POSITIONS,
    ALL_POKER_STAGES,
    MIN_NUM_PLAYERS,
    MAX_NUM_PLAYERS,
    BOARD_NUM_CARDS,
    PokerStage,
)
from .components.card import PokerCard, PokerBoard
from .poker_player import PokerPlayer, PlayerAction, PlayerStatus
from .components.rules import rank_hands


CARD_DECK_SIZE = 52


class PokerTable:
    cards: List[PokerCard]
    board: PokerBoard
    players: List[Optional[PokerPlayer]]
    eliminated_players: Dict[PokerPlayer, int]
    button: int
    stage: PokerStage
    big_blind: float
    small_blind: float
    min_buy_in: float
    max_buy_in: float
    hand_number: int
    per_player_action: Dict[PokerStage, List[List[Tuple[PlayerAction, float]]]]

    def __init__(
        self,
        num_players: int,
        big_blind: float,
        small_blind: float,
        min_buy_in: float,
        max_buy_in: float,
    ):
        self.cards = [
            PokerCard(card_str[0], card_str[1]) for card_str in POKER_CARD_DECK
        ]
        assert len(self.cards) == CARD_DECK_SIZE
        assert num_players >= MIN_NUM_PLAYERS and num_players <= MAX_NUM_PLAYERS
        self.board = [None] * BOARD_NUM_CARDS
        self.players = [None for _ in range(num_players)]
        self.num_players = num_players
        self.eliminated_players = {}
        self.button = np.random.choice(np.arange(self.num_players))
        self.player_in_action = self.button + 3
        self.pot = 0
        self.big_blind = big_blind
        self.small_blind = small_blind
        self.min_buy_in = min_buy_in
        self.max_buy_in = max_buy_in
        self.hand_number = 0
        self._reset()

    def _move_button(self):
        # Move button
        self.button = (self.button + 1) % self.num_players
        button_player = self.players[self.button]
        while button_player is None or not button_player.is_playing():
            self.button = (self.button + 1) % self.num_players
            button_player = self.players[self.button]

    def _assign_positions(self):
        # Assign positions for active players
        button_idx = self.button
        assert self.get_curr_hand_num_players() >= MIN_NUM_PLAYERS
        # TODO (hkwark): Need to wait for sitting out players to come back to start the game
        num_curr_players = self.get_curr_hand_num_players()
        player_positions = NUM_PLAYERS_TO_POSITIONS[num_curr_players]
        count = 0
        for i in range(1, self.num_players + 1):
            idx = (button_idx + i) % self.num_players
            player = self.players[idx]
            if player is not None and player.is_playing():
                player.position = player_positions[count]
                count += 1
        assert count == len(player_positions)

    def _next(self):
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

    def _reset(self):
        for player in self.players:
            if player is None:
                continue
            player.reset_hand()
            if np.isclose(player.stack, 0):
                # Ask player to buy in
                buy_in = np.random.uniform(low=self.min_buy_in, high=self.max_buy_in)
                player.buy_in(buy_in)
        self.per_player_action = {
            stage: [[] for _ in range(self.num_players)] for stage in ALL_POKER_STAGES
        }
        self.stage = PokerStage.PREFLOP

    def _blind(self):
        small_blind = self.players[self.player_in_action]
        assert small_blind is not None
        bet = small_blind.blind(self.small_blind, self.big_blind)
        self.per_player_action[self.stage][self.player_in_action].append(
            (PlayerAction.SMALL_BLIND, bet)
        )
        self._next()

        big_blind = self.players[self.player_in_action]
        assert big_blind is not None
        bet = big_blind.blind(self.big_blind, self.big_blind)
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
        if self.get_num_active_players() > 0:
            straddle_player = self.players[self.player_in_action]
            assert straddle_player is not None
            if straddle_player.straddle(
                self.get_player_stacks(), self.player_in_action, self.big_blind
            ):
                self.per_player_action[self.stage][self.player_in_action].append(
                    (PlayerAction.STRADDLE, 2 * self.big_blind)
                )
                self._next()

    def _shuffle(self) -> List[PokerCard]:
        assert len(self.cards) == CARD_DECK_SIZE
        np.random.shuffle(self.cards)  # type: ignore
        return self.cards.copy()

    def _deal(self, card_deck: List[PokerCard]):
        first_hands = []
        for i in range(self.get_curr_hand_num_players()):
            first_hands.append(card_deck.pop())
        second_hands = []
        for i in range(self.get_curr_hand_num_players()):
            second_hands.append(card_deck.pop())

        count = 0
        for player_idx in range(self.button + 1, self.button + self.num_players + 1):
            player = self.players[player_idx % self.num_players]
            if player is not None and player.is_playing():
                player.get_card((first_hands[count], second_hands[count]))
                count += 1
        assert count == len(first_hands) == len(second_hands)

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

    def _action(self):
        while not self._action_finished():
            curr_player = self.players[self.player_in_action]
            assert curr_player is not None
            assert curr_player.stack > 0, curr_player.stack
            bet, action = curr_player.action(
                self.board,
                self.per_player_action,
                self.get_player_stacks(),
                self.player_in_action,
                self.big_blind,
            )
            self.per_player_action[self.stage][self.player_in_action].append(
                (action, bet)
            )
            if action == PlayerAction.RAISE:
                for player in self.players:
                    if (
                        player is None
                        or player == curr_player
                        or not player.is_active()
                    ):
                        continue
                    else:
                        player.status = PlayerStatus.WAITING_TURN
            self._next()

    def _end_stage(self, river: bool = False):
        # Done with all betting actions. Prepare for next stage
        for player in self.players:
            if player is not None and player.is_active():
                player.status = (
                    PlayerStatus.CALL if river else PlayerStatus.WAITING_TURN
                )
            else:
                continue

    def _eliminate_players(self):
        for i, player in enumerate(self.players):
            if player is None:
                continue
            else:
                assert player.stack >= 0, (player.name, player.stack)
                if np.isclose(player.stack, 0):
                    # TODO: Try to Buy In Player with a random amount
                    player.status = PlayerStatus.SITTING_OUT
                    if player.left_num_buy_ins == 0:
                        player.status = PlayerStatus.ELIMINATED
                    if player.is_eliminated() and player not in self.eliminated_players:
                        # Eliminate Player
                        self.eliminated_players[player] = self.hand_number
                        self.players[i] = None
                        continue

    def get_num_live_players(self) -> int:
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

    def get_curr_hand_num_players(self) -> int:
        """
        get number of players that have received a hand. (Participated in current hand)
        """
        num_hand_players = 0
        for player in self.players:
            if player is not None and player.is_playing():
                num_hand_players += 1
        return num_hand_players

    def get_live_players(self) -> List[PokerPlayer]:
        """
        get number of players surviving. (Not eliminated)
        """
        live_players = []
        for player in self.players:
            if player is not None and not player.is_eliminated():
                live_players.append(player)
        return live_players

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

    def preflop(self):
        assert self.get_num_active_players() >= MIN_NUM_PLAYERS
        assert self.get_num_active_players() == self.get_curr_hand_num_players()
        self.stage = PokerStage.PREFLOP
        self.player_in_action = self.button
        self._next()
        self._blind()
        self._straddle()
        active_card_deck = self._shuffle()
        self._deal(active_card_deck)
        self._action()
        self._end_stage()
        return active_card_deck

    def flop(self, card_deck: List[PokerCard]):
        assert len(card_deck) == CARD_DECK_SIZE - 2 * self.get_curr_hand_num_players()
        self.stage = PokerStage.FLOP
        card_deck.pop()
        for i in range(3):
            self.board[i] = card_deck.pop()
        self.player_in_action = self.button
        self._next()
        self._action()
        self._end_stage()

    def turn(self, card_deck: List[PokerCard]):
        assert (
            len(card_deck) == CARD_DECK_SIZE - 2 * self.get_curr_hand_num_players() - 4
        )
        self.stage = PokerStage.TURN
        card_deck.pop()
        self.board[3] = card_deck.pop()
        self.player_in_action = self.button
        self._next()
        self._action()
        self._end_stage()

    def river(self, card_deck: List[PokerCard]):
        assert (
            len(card_deck) == CARD_DECK_SIZE - 2 * self.get_curr_hand_num_players() - 6
        )
        self.stage = PokerStage.RIVER
        card_deck.pop()
        self.board[4] = card_deck.pop()
        self.player_in_action = self.button
        self._next()
        self._action()
        self._end_stage(river=True)

    def cashing(self):
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

    def play_hand(self):
        self.hand_number += 1
        self._reset()
        self._assign_positions()
        active_card_deck = self.preflop()
        self.flop(active_card_deck)
        self.turn(active_card_deck)
        self.river(active_card_deck)
        self.cashing()
        self._eliminate_players()
        self._move_button()

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
        assert (
            not new_player.is_eliminated()
        ), f"Cannot seat an eliminated player {new_player}"
        for i, player in enumerate(self.players):
            if player is None:
                empty_seats.append(i)
        success = len(empty_seats) > 0
        if success:
            seat = np.random.choice(empty_seats)
            self.players[seat] = new_player
        return success

    def update_blind(self, small_blind: float, big_blind: float):
        self.small_blind = small_blind
        self.big_blind = big_blind

    def finished(self):
        return self.get_num_live_players() < MIN_NUM_PLAYERS

    def player_rankings(self) -> List[PokerPlayer]:
        num_alive = self.get_num_live_players()
        # sort by remaining stack if not eliminated
        live_players = self.get_live_players()

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

        for player in self.get_live_players():
            assert player not in self.eliminated_players
            report[player] = {}
            report[player]["name"] = player.name
            report[player]["stack"] = player.stack
            report[player]["num_hands_played"] = self.hand_number

        report_str = ""
        for i, player in enumerate(self.player_rankings(), 1):
            report_str += f"{i}. {report[player]}\n"
        return report, report_str
