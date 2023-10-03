import numpy as np

from typing import Optional, List, Tuple
from .card import PokerHole, PokerBoard
from .agents import PlayerAction

MAX_HAND_CACHE_SIZE = 10


class PokerPlayer:
    name: str
    left_num_buy_ins: int
    stack: float
    last_action: PlayerAction
    _hole: Optional[PokerHole]
    eliminated: bool = False
    _past_hands: List[PokerHole] = []

    def __init__(self, name: str, buy_in: float, num_buy_ins: int):
        self.name = name
        self.stack = buy_in
        self.left_num_buy_ins = num_buy_ins
        self._hole = None
        # self.action_agent = action_agent

    def get_card(self, hole: PokerHole):
        assert self._hole is None
        self._hole = hole

    def get_effective_stack(self, big_blind: float) -> float:
        return self.stack / big_blind

    def action(
        self,
        board: PokerBoard,
        per_player_bet: List[float],
        per_player_state: List[List[PlayerAction]],
        big_blind: float,
        button_position: int,
        my_position: int,
    ) -> Tuple[float, PlayerAction]:
        assert len(board) == 5
        action = PlayerAction.CALL
        bet = np.max(per_player_bet) - per_player_bet[my_position]
        prev_bet = 0.0
        if action == PlayerAction.RAISE:
            assert bet >= prev_bet + big_blind
        if self.stack < bet:
            action = PlayerAction.CALL
            bet = self.stack
        self.last_action = action
        self.stack = self.stack - bet
        return bet, action

    def open_cards(self) -> PokerHole:
        assert self._hole is not None
        return self._hole

    def cash(self, cash_size: float):
        assert self.stack >= 0 and cash_size >= 0
        self.stack += cash_size

    def buy_in(self, buy_in: float):
        assert self.stack == 0
        if self.left_num_buy_ins == 0:
            self.eliminated = True
            self.last_action = PlayerAction.FOLD
        else:
            self.left_num_buy_ins = self.left_num_buy_ins - 1
            self.stack += buy_in
            self.last_action = PlayerAction.WAITING

    def reset_hand(self):
        self._hole = None
        if not self.eliminated:
            self.last_action = PlayerAction.WAITING
        else:
            self.last_action = PlayerAction.FOLD

    def blind(self, blind: float) -> float:
        assert self.stack > 0
        if self.stack < blind:
            self.last_action = PlayerAction.CALL
        else:
            self.last_action = PlayerAction.WAITING
        blind_val = min(self.stack, blind)
        self.stack = self.stack - blind_val
        return blind_val

    def straddle(self, villain_stacks: List[float], big_blind: float) -> bool:
        straddle = False
        if straddle:
            self.last_action = PlayerAction.WAITING
        return straddle

    def is_all_in(self):
        return self.stack == 0 and self.last_action == PlayerAction.CALL

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return str.__hash__(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
