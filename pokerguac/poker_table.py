import numpy as np

from typing import List, Dict, Optional

from .agents import PlayerAction
from .poker.constants import POKER_CARD_DECK
from .poker.player import PokerPlayer
from .poker.card import PokerCard, PokerBoard
from .poker.rules import rank_hands


CARD_DECK_SIZE = 52
MIN_NUM_PLAYERS = 2


class PokerTable:
    cards: List[PokerCard]
    board: PokerBoard
    players: List[Optional[PokerPlayer]]
    eliminated_players: Dict[PokerPlayer, int]
    button: int
    big_blind: float
    small_blind: float
    min_buy_in: float
    max_buy_in: float
    hand_number: int
    per_player_bet: np.ndarray
    per_player_action: List[List[PlayerAction]]

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
        self.board = [None, None, None, None, None]
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
        self.button = (self.button + 1) % self.num_players
        button_player = self.players[self.button]
        while button_player is None or button_player.eliminated:
            self.button = (self.button + 1) % self.num_players
            button_player = self.players[self.button]

    def _get_big_blind_position(self):
        count = 0
        index = self.button
        while count < 2:
            index = (index + 1) % self.num_players
            player = self.players[index]
            if player is not None and not player.eliminated:
                count += 1
        return index

    def _next(self):
        self.player_in_action = (self.player_in_action + 1) % self.num_players
        curr_player = self.players[self.player_in_action]
        while (
            curr_player is None
            or curr_player.is_all_in()
            or not (
                curr_player.last_action == PlayerAction.WAITING
                or curr_player.last_action == PlayerAction.CALL
                or curr_player.last_action == PlayerAction.RAISE
            )
        ):
            self.player_in_action = (self.player_in_action + 1) % self.num_players
            curr_player = self.players[self.player_in_action]

    def _reset(self):
        for player in self.players:
            if player is None:
                continue
            player.reset_hand()
        self.per_player_bet = np.zeros(self.num_players)
        self.per_player_action = [[] for _ in range(self.num_players)]

    def _blind(self):
        small_blind = self.players[self.player_in_action]
        assert small_blind is not None
        bet = small_blind.blind(self.small_blind)
        self.per_player_bet[self.player_in_action] += bet
        self.per_player_action[self.player_in_action].append(PlayerAction.SMALL_BLIND)
        self._next()

        big_blind = self.players[self.player_in_action]
        assert big_blind is not None
        bet = big_blind.blind(self.big_blind)
        self.per_player_bet[self.player_in_action] += bet
        self.per_player_action[self.player_in_action].append(PlayerAction.BIG_BLIND)
        self._next()

    def _straddle(self):
        straddle_player = self.players[self.player_in_action]
        assert straddle_player is not None
        stacks = []
        for i in range(self.num_players):
            player = self.players[i]
            if player is None:
                stacks.append(0.0)
            else:
                stacks.append(player.stack)

        other_stacks = (
            stacks[: self.player_in_action] + stacks[self.player_in_action + 1 :]
        )
        if straddle_player.straddle(other_stacks, self.big_blind):
            self.per_player_bet[self.player_in_action] += 2 * self.big_blind
            self.per_player_action[self.player_in_action].append(PlayerAction.STRADDLE)
            self._next()

    def _shuffle(self) -> List[PokerCard]:
        assert len(self.cards) == CARD_DECK_SIZE
        np.random.shuffle(self.cards)  # type: ignore
        return self.cards.copy()

    def _deal(self, card_deck: List[PokerCard]):
        first_hands = []
        num_out_players = 0
        for player in self.players:
            if player is None or player.eliminated:
                num_out_players += 1
        for i in range(self.num_players - num_out_players):
            first_hands.append(card_deck.pop())
        second_hands = []
        for i in range(self.num_players - num_out_players):
            second_hands.append(card_deck.pop())

        count = 0
        for player_idx in range(self.button + 1, self.button + self.num_players + 1):
            player = self.players[player_idx % self.num_players]
            if player is not None and not player.eliminated:
                player.get_card((first_hands[count], second_hands[count]))
                count += 1
        assert count == len(first_hands) == len(second_hands)

    def _action_finished(self):
        action_finished = True
        raise_counter = 0
        for player in self.players:
            if player is None:
                continue
            elif player.last_action == PlayerAction.WAITING:
                action_finished = False
            elif player.last_action == PlayerAction.RAISE:
                raise_counter += 1
            elif player.last_action == PlayerAction.STRADDLE:
                raise_counter += 1

        if raise_counter >= 2:
            action_finished = False

        return action_finished

    def _action(self):
        while not self._action_finished():
            player = self.players[self.player_in_action]
            assert player is not None
            assert player.stack > 0, player.stack
            bet, action = player.action(
                self.board,
                self.per_player_bet,
                self.per_player_action,
                self.big_blind,
                self.button,
                self.player_in_action,
            )
            self.per_player_bet[self.player_in_action] += bet
            self.per_player_action[self.player_in_action].append(action)
            if action == PlayerAction.RAISE:
                for player in self.players:
                    if (
                        player is None
                        or player.last_action == PlayerAction.FOLD
                        or player.is_all_in()
                    ):
                        continue
                    else:
                        player.last_action = PlayerAction.WAITING
            self._next()

    def _end_stage(self):
        # Done with all betting actions. Prepare for next stage
        for player in self.players:
            if player is None or player.eliminated:
                continue
            elif player.is_all_in():
                assert player.last_action == PlayerAction.CALL
            elif player.last_action is not PlayerAction.FOLD:
                player.last_action = PlayerAction.WAITING

    def _eliminate_players(self):
        for i, player in enumerate(self.players):
            if player is None:
                continue
            else:
                assert player.stack >= 0, player.stack
                if player.stack == 0:
                    # Buy In Player
                    player.buy_in(
                        np.random.uniform(low=self.min_buy_in, high=self.max_buy_in)
                    )
                    if player.eliminated and player not in self.eliminated_players:
                        # Eliminate Player
                        self.eliminated_players[player] = self.hand_number
                        self.players[i] = None
                        continue

    def get_num_live_players(self) -> int:
        num_out_players = 0
        for player in self.players:
            if player is None or player.eliminated:
                num_out_players += 1
        num_alive_players = self.num_players - num_out_players
        return num_alive_players

    def get_live_players(self) -> List[PokerPlayer]:
        live_players = []
        for player in self.players:
            if player is not None and not player.eliminated:
                live_players.append(player)
        return live_players

    def preflop(self):
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
        assert len(card_deck) == CARD_DECK_SIZE - 2 * self.get_num_live_players()
        card_deck.pop()
        for i in range(3):
            self.board[i] = card_deck.pop()
        self.player_in_action = self.button
        self._next()
        self._action()
        self._end_stage()

    def turn(self, card_deck: List[PokerCard]):
        assert len(card_deck) == CARD_DECK_SIZE - 2 * self.get_num_live_players() - 4
        card_deck.pop()
        self.board[3] = card_deck.pop()
        self.player_in_action = self.button
        self._next()
        self._action()
        self._end_stage()

    def river(self, card_deck: List[PokerCard]):
        assert len(card_deck) == CARD_DECK_SIZE - 2 * self.get_num_live_players() - 6
        card_deck.pop()
        self.board[4] = card_deck.pop()
        self.player_in_action = self.button
        self._next()
        self._action()

    def cashing(self):
        player_holes = []
        candidate_players = []
        for player in self.players:
            if player is None:
                continue
            elif player.last_action == PlayerAction.CALL:
                player_holes.append(player.open_cards())
                candidate_players.append(player)

        player_ranks = rank_hands(self.board, player_holes)
        ranked_players = {}
        for rank, player in zip(player_ranks, candidate_players):
            if rank in ranked_players:
                ranked_players[rank].append(self.players.index(player))
            else:
                ranked_players[rank] = [self.players.index(player)]

        for rank in sorted(ranked_players.keys()):
            total_pot = self.get_pot_size()
            if total_pot == 0:
                break
            elif total_pot < 0:
                raise ValueError(
                    f"Something is going wrong with cashing out! Total pot size {total_pot} is different from total prize"
                )
            else:
                num_ties = len(ranked_players[rank])
                players = [self.players[i] for i in ranked_players[rank]]
                bets = np.array([self.per_player_bet[i] for i in ranked_players[rank]])
                players_and_bets = sorted(zip(players, bets), key=lambda x: x[1])
                players, bets = [x[0] for x in players_and_bets], [
                    x[1] for x in players_and_bets
                ]
                bets = np.array([0] + bets)
                bets = bets[1:] - bets[:-1]
                rank_cashed_outs = np.zeros(self.num_players)
                for i, player in enumerate(players):
                    cashed_out_bets = np.zeros(self.num_players)
                    per_player_bets = self.per_player_bet
                    for j in range(i + 1):
                        player_pots = np.minimum(bets[j], per_player_bets)
                        cashed_out_bets += player_pots / (num_ties - j)
                        per_player_bets = per_player_bets - player_pots
                    rank_cashed_outs += cashed_out_bets
                    player.cash(np.sum(cashed_out_bets))
                self.per_player_bet = self.per_player_bet - rank_cashed_outs

        assert np.allclose(
            self.per_player_bet, np.zeros(self.num_players), rtol=1e-5, atol=1e-10
        )
        self.per_player_bet = np.zeros(self.num_players)

    def play_hand(self):
        self.hand_number += 1
        active_card_deck = self.preflop()
        self.flop(active_card_deck)
        self.turn(active_card_deck)
        self.river(active_card_deck)
        self.cashing()
        self._eliminate_players()
        self._reset()
        self._move_button()

    def get_pot_size(self) -> float:
        return np.sum(self.per_player_bet)

    def seat_player(self, new_player: PokerPlayer) -> bool:
        empty_seats = []
        assert (
            not new_player.eliminated
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

    def player_rankings(self):
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

    def player_rankings_report(self):
        report = {}
        for player in self.eliminated_players:
            report[player] = {}
            report[player]["name"] = player.name
            report[player]["stack"] = player.stack
            assert player.stack == 0
            report[player]["num_hands_played"] = self.eliminated_players[player]

        for player in self.get_live_players():
            assert player not in self.eliminated_players
            report[player] = {}
            report[player]["name"] = player.name
            report[player]["stack"] = player.stack
            report[player]["num_hands_played"] = self.hand_number
        return report
