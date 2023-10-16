import numpy as np

from typing import Optional, List, Tuple
from .components.card import PokerHole, PokerBoard
from .components.constants import PlayerAction, PlayerPosition, PlayerStatus
from .agents.poker_agent import PokerAgent

MAX_HAND_CACHE_SIZE = 10


class PokerPlayer:
    name: str
    left_num_buy_ins: int
    stack: float
    position: PlayerPosition
    last_action: PlayerAction
    status: PlayerStatus
    _hole: Optional[PokerHole]
    _past_hands: List[PokerHole] = []

    def __init__(self, name: str, num_buy_ins: int, action_agent: PokerAgent):
        self.name = name
        self.stack = 0
        self.left_num_buy_ins = num_buy_ins
        self._hole = None
        self.last_action = PlayerAction.FOLD
        self.status = PlayerStatus.WAITING_HAND
        self.action_agent = action_agent
        self.total_buy_in = 0

    def get_card(self, hole: PokerHole):
        assert self._hole is None
        self._hole = hole

    def get_effective_stack(self, big_blind: float) -> float:
        return self.stack / big_blind

    def action(
        self,
        board: PokerBoard,
        per_player_bet: np.ndarray,
        per_player_action: List[List[Tuple[PlayerAction, float]]],
        big_blind: float,
        button_pos: int,
        player_pos: int,
    ) -> Tuple[float, PlayerAction]:
        assert len(board) == 5
        assert len(per_player_bet) == len(per_player_action)
        bet, action = self.action_agent.action(
            board,
            per_player_bet,
            per_player_action,
            big_blind,
            button_pos,
            player_pos,
            self.stack,
        )
        assert (
            self.stack >= bet
        ), f"Invalid betting occured from player {self.name}: [stack: {self.stack}, bet: {bet}]"

        if action == PlayerAction.RAISE:
            self.status = PlayerStatus.RAISE
            if not bet == self.stack:
                assert (
                    per_player_bet[player_pos] + bet - np.max(per_player_bet)
                    >= big_blind
                ), (big_blind, bet, per_player_bet)
        elif action == PlayerAction.FOLD:
            self.status = PlayerStatus.FOLD
            assert bet == 0
        else:
            self.status = PlayerStatus.CALL
        self.last_action = action
        self.stack = self.stack - bet

        return bet, action

    def open_cards(self) -> PokerHole:
        assert self._hole is not None
        return self._hole

    def cash(self, cash_size: float):
        assert self.stack >= 0 and cash_size >= 0, (self.stack, cash_size)
        self.stack += cash_size

    def buy_in(self, buy_in: float):
        assert self.stack == 0
        if self.left_num_buy_ins > 0:
            self.total_buy_in = self.total_buy_in + buy_in
            self.left_num_buy_ins = self.left_num_buy_ins - 1
            self.stack += buy_in
        else:
            self.last_action = PlayerAction.FOLD
            self.status = PlayerStatus.SITTING_OUT

    def reset_hand(self):
        self._hole = None
        if self.is_eliminated() or self.status == PlayerStatus.SITTING_OUT:
            self.last_action = PlayerAction.FOLD
            self.status = PlayerStatus.SITTING_OUT
        else:
            self.last_action = PlayerAction.CALL
            self.status = PlayerStatus.WAITING_TURN

    def blind(self, small_blind: float, big_blind: float) -> float:
        assert self.stack > 0
        assert (
            self.position == PlayerPosition.SMALLBLIND
            or self.position == PlayerPosition.BIGBLIND
        )
        big = self.position == PlayerPosition.BIGBLIND
        self.last_action = PlayerAction.BIG_BLIND if big else PlayerAction.SMALL_BLIND

        blind = big_blind if big else small_blind
        if self.stack <= small_blind:
            self.status = PlayerStatus.CALL
        else:
            self.status = PlayerStatus.RAISE
        blind_val = min(self.stack, blind)
        self.stack = self.stack - blind_val
        return blind_val

    def straddle(self, villain_stacks: List[float], big_blind: float) -> bool:
        if self.stack < 2 * big_blind:
            straddle = False
        else:
            straddle = False
        if straddle:
            self.last_action = PlayerAction.STRADDLE
            self.status = PlayerStatus.RAISE
            self.stack = self.stack - 2 * big_blind
        return straddle

    def net_profit(self):
        return self.stack - self.total_buy_in

    def is_sitting_out(self):
        return self.status == PlayerStatus.SITTING_OUT

    def is_all_in(self):
        return (
            self.stack == 0
            and self.status != PlayerStatus.FOLD
            and self.status != PlayerStatus.SITTING_OUT
        )

    def is_eliminated(self):
        return (
            self.left_num_buy_ins == 0
            and self.stack == 0
            and self.last_action == PlayerAction.FOLD
            and PlayerStatus.SITTING_OUT
        )

    def is_active(self):
        """
        Player is at an actionable state. (Can Raise)
        """
        return (
            self.status != PlayerStatus.FOLD
            and not self.is_eliminated()
            and not self.is_sitting_out()
            and not self.is_all_in()
        )

    def is_alive(self):
        """
        Player is still participating in the current hand (but can be all-in)
        """
        return (
            self.status != PlayerStatus.FOLD
            and not self.is_eliminated()
            and not self.is_sitting_out()
        )

    def is_playing(self):
        """
        Player is still playing the game (in a state that the player can receive a new hand)
        """
        return not self.is_eliminated() and not self.is_sitting_out()

    def __eq__(self, other):
        if isinstance(other, PokerPlayer):
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return str.__hash__(self.name)

    def __str__(self):
        return f"{self.name} ({self.position}): {self.stack}"

    def __repr__(self):
        return self.__str__()
