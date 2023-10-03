import numpy as np

from typing import List, Dict

from .constants import POKER_CARD_DECK
from .player import PokerPlayer
from .agents import PlayerAction
from .card import PokerCard, PokerBoard
from .rules import rank_hands


MAX_NUM_PLAYERS = 9
MIN_NUM_PLAYERS = 2
CARD_DECK_SIZE = 52


class PokerTable:
    cards: List[PokerCard]
    board: PokerBoard
    players: List[PokerPlayer]
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
        players: List[PokerPlayer],
        big_blind: float,
        small_blind: float,
        min_buy_in: float,
        max_buy_in: float,
    ):
        self.cards = [
            PokerCard(card_str[0], card_str[1]) for card_str in POKER_CARD_DECK
        ]
        assert len(self.cards) == CARD_DECK_SIZE
        assert len(players) <= MAX_NUM_PLAYERS and len(players) >= MIN_NUM_PLAYERS
        self.board = [None, None, None, None, None]
        self.players = players
        self.eliminated_players = {}
        self.button = np.random.choice(np.arange(len(self.players)))
        self.player_in_action = self.button + 3
        self.pot = 0
        self.big_blind = big_blind
        self.small_blind = small_blind
        self.min_buy_in = min_buy_in
        self.max_buy_in = max_buy_in
        self.hand_number = 0
        self._reset()

    def _move_button(self):
        self.button = (self.button + 1) % len(self.players)
        while self.players[self.button].eliminated:
            self.button = (self.button + 1) % len(self.players)

    def _get_big_blind_position(self):
        count = 0
        index = self.button
        while count < 2:
            index = (index + 1) % len(self.players)
            if not self.players[index].eliminated:
                count += 1
        return index

    def _next(self):
        self.player_in_action = (self.player_in_action + 1) % len(self.players)
        while not (
            self.players[self.player_in_action].last_action == PlayerAction.WAITING
            or self.players[self.player_in_action].last_action == PlayerAction.CALL
            or self.players[self.player_in_action].last_action == PlayerAction.RAISE
        ):
            self.player_in_action = (self.player_in_action + 1) % len(self.players)

    def _reset(self):
        for player in self.players:
            player.reset_hand()
        self.per_player_bet = np.zeros(len(self.players))
        self.per_player_action = [[] for _ in range(len(self.players))]

    def _blind(self):
        small_blind = self.players[self.player_in_action]
        bet = small_blind.blind(self.small_blind)
        self.per_player_bet[self.player_in_action] += bet
        self.per_player_action[self.player_in_action].append(PlayerAction.SMALL_BLIND)
        self._next()

        big_blind = self.players[self.player_in_action]
        bet = big_blind.blind(self.big_blind)
        self.per_player_bet[self.player_in_action] += bet
        self.per_player_action[self.player_in_action].append(PlayerAction.BIG_BLIND)
        self._next()

    def _straddle(self):
        straddle_player = self.players[self.player_in_action]
        stacks = [self.players[i].stack for i in range(len(self.players))]
        other_stacks = (
            stacks[: self.player_in_action] + stacks[self.player_in_action + 1 :]
        )
        if straddle_player.straddle(other_stacks, self.big_blind):
            self.per_player_bet[self.player_in_action] += 2 * self.big_blind
            self.per_player_action[self.player_in_action].append(PlayerAction.STRADDLE)
            self._next()

    def _shuffle(self) -> List[PokerCard]:
        assert len(self.cards) == CARD_DECK_SIZE
        np.random.shuffle(self.cards)
        return self.cards.copy()

    def _deal(self, card_deck: List[PokerCard]):
        first_hands = []
        for i in range(len(self.players) - len(self.eliminated_players)):
            first_hands.append(card_deck.pop())
        second_hands = []
        for i in range(len(self.players) - len(self.eliminated_players)):
            second_hands.append(card_deck.pop())

        count = 0
        for player_idx in range(self.button + 1, self.button + len(self.players) + 1):
            player_idx = player_idx % len(self.players)
            if not self.players[player_idx].eliminated:
                self.players[player_idx].get_card(
                    (first_hands[count], second_hands[count])
                )
                count += 1
        assert count == len(first_hands) == len(second_hands)

    def _bet_finished(self):
        bet_finished = True
        raise_counter = 0
        for player in self.players:
            if player.last_action == PlayerAction.WAITING:
                bet_finished = False
            elif player.last_action == PlayerAction.RAISE:
                raise_counter += 1
        if raise_counter >= 2:
            bet_finished = False

        return bet_finished

    def _action(self):
        while not self._bet_finished():
            player = self.players[self.player_in_action]
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
                assert bet >= self.big_blind
                for player in self.players:
                    if (
                        player.last_action == PlayerAction.CALL
                        or player.last_action == PlayerAction.RAISE
                    ):
                        player.last_action = PlayerAction.WAITING
            self._next()

    def _end_stage(self):
        # Done with all betting actions. Prepare for next stage
        for player in self.players:
            if not player.eliminated and player.last_action is not PlayerAction.FOLD:
                player.last_action = PlayerAction.WAITING

    def _eliminate_players(self):
        for player in self.players:
            assert player.stack >= 0, player.stack
            if player.stack == 0:
                # Buy In Player
                player.buy_in(
                    np.random.uniform(low=self.min_buy_in, high=self.max_buy_in)
                )
                if player.eliminated and player not in self.eliminated_players:
                    # Eliminate Player
                    self.eliminated_players[player] = self.hand_number
                    continue

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
        num_alive_players = len(self.players) - len(self.eliminated_players)
        assert len(card_deck) == CARD_DECK_SIZE - 2 * num_alive_players
        card_deck.pop()
        for i in range(3):
            self.board[i] = card_deck.pop()
        self.player_in_action = self.button
        self._next()
        self._action()
        self._end_stage()

    def turn(self, card_deck: List[PokerCard]):
        num_alive_players = len(self.players) - len(self.eliminated_players)
        assert len(card_deck) == CARD_DECK_SIZE - 2 * num_alive_players - 4
        card_deck.pop()
        self.board[3] = card_deck.pop()
        self.player_in_action = self.button
        self._next()
        self._action()
        self._end_stage()

    def river(self, card_deck: List[PokerCard]):
        num_alive_players = len(self.players) - len(self.eliminated_players)
        assert len(card_deck) == CARD_DECK_SIZE - 2 * num_alive_players - 6
        card_deck.pop()
        self.board[4] = card_deck.pop()
        self.player_in_action = self.button
        self._next()
        self._action()

    def cashing(self):
        player_holes = []
        candidate_players = []
        for player in self.players:
            if player.last_action == PlayerAction.CALL or player.is_all_in():
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
                rank_cashed_outs = np.zeros(len(self.players))
                for i, player in enumerate(players):
                    cashed_out_bets = np.zeros(len(self.players))
                    per_player_bets = self.per_player_bet
                    for j in range(i + 1):
                        player_pots = np.minimum(bets[j], per_player_bets)
                        cashed_out_bets += player_pots / (num_ties - j)
                        per_player_bets = per_player_bets - player_pots
                    rank_cashed_outs += cashed_out_bets
                    player.cash(np.sum(cashed_out_bets))
                self.per_player_bet = self.per_player_bet - rank_cashed_outs

        assert np.allclose(
            self.per_player_bet, np.zeros(len(self.players)), rtol=1e-5, atol=1e-10
        )
        self.per_player_bet = np.zeros(len(self.players))

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

    def update_blind(self, small_blind: float, big_blind: float):
        self.small_blind = small_blind
        self.big_blind = big_blind

    def finished(self):
        count_dead = 0
        for player in self.players:
            if player.eliminated:
                count_dead += 1
        assert count_dead < len(self.players)
        return count_dead == len(self.players) - 1

    def player_rankings(self):
        num_alive = len(self.players) - len(self.eliminated_players)
        # sort by remaining stack if not eliminated
        player_rankings = (
            sorted(
                self.eliminated_players.keys(),
                key=lambda x: self.eliminated_players[x],
            )
            + sorted(self.players, key=lambda x: x.stack)[-num_alive:]
        )
        player_rankings.reverse()
        return player_rankings

    def player_rankings_report(self):
        report = {}
        for player in self.players:
            report[player] = {}
            report[player]["name"] = player.name
            report[player]["stack"] = player.stack
            if player in self.eliminated_players:
                report[player]["num_hands_played"] = self.eliminated_players[player]
            else:
                report[player]["num_hands_played"] = self.hand_number
        return report
