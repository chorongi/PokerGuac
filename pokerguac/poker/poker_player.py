import numpy as np
from queue import Queue
from typing import Optional, List, Dict, Tuple, Sequence
from .components.card import PokerBoard, PokerHole, PokerCard
from .components.constants import (
    PlayerAction,
    PlayerPosition,
    PlayerStatus,
    PokerStage,
    PlayerType,
    ALL_POKER_STAGES,
    INVALID_NAMES,
)
from .agents.poker_agent import PokerAgent


class PokerPlayer:
    name: str
    stack: float
    position: Optional[PlayerPosition]
    hole: Optional[PokerHole]
    status: PlayerStatus
    stage_bet: float
    bank_roll: float
    start_bank_roll: float
    time_bank: Optional[float] = None
    left_num_buy_ins: Optional[int] = None
    type: PlayerType

    def __init__(self, name: str, action_agent: PokerAgent, bank_roll: float):
        assert name.lower() not in INVALID_NAMES
        self.name = name
        self.action_agent = action_agent
        self.bank_roll = bank_roll
        self.start_bank_roll = bank_roll
        self.stack = 0
        self.reset()

    def reset(self):
        self.stage_bet = 0
        self.hole = None
        self.status = PlayerStatus.SITTING_OUT
        self.position = None

    def stage_reset(self, stage: PokerStage):
        self.stage_bet = 0
        if self.is_active():
            self.status = (
                PlayerStatus.CALL
                if stage == PokerStage.RIVER
                else PlayerStatus.WAITING_TURN
            )

    def hand_reset(self):
        self.hole = None
        if not self.is_eliminated() or not self.is_sitting_out():
            self.status = PlayerStatus.WAITING_TURN

    def set_card(self, hole: PokerHole):
        assert self.hole is None
        self.hole = hole

    def get_effective_stack(self, big_blind: float) -> float:
        return self.stack / big_blind

    @classmethod
    def per_player_action_to_bet(
        cls,
        per_player_action: Dict[PokerStage, List[List[Tuple[PlayerAction, float]]]],
    ) -> np.ndarray:
        total_bets = np.zeros(len(per_player_action[PokerStage.PREFLOP]))
        for stage in ALL_POKER_STAGES:
            for i in range(len(per_player_action[stage])):
                for action, bet in per_player_action[stage][i]:
                    total_bets[i] += bet
        return total_bets

    def action(
        self,
        board: PokerBoard,
        per_player_action: Dict[PokerStage, List[List[Tuple[PlayerAction, float]]]],
        player_stacks: List[float],
        player_idx: int,
        big_blind: float,
    ) -> Tuple[float, PlayerAction]:
        assert len(board) == 5
        assert self.position is not None
        bet, action = self.action_agent.action(
            board,
            self.per_player_action_to_bet(per_player_action),
            per_player_action,
            player_stacks,
            self.position,
            player_idx,
            big_blind,
        )
        assert (
            self.stack >= bet
        ), f"Invalid betting occured from player {self.name}: [stack: {self.stack}, bet: {bet}]"
        per_player_bet = self.per_player_action_to_bet(per_player_action)

        if action == PlayerAction.RAISE:
            self.status = PlayerStatus.RAISE
            if not bet == self.stack:
                assert (
                    per_player_bet[player_idx] + bet - np.max(per_player_bet)
                    >= big_blind
                ), (big_blind, bet, per_player_bet)
        elif action == PlayerAction.FOLD:
            self.status = PlayerStatus.FOLD
            assert bet == 0
        else:
            self.status = PlayerStatus.CALL
        self.stack = self.stack - bet
        self.stage_bet += bet

        return bet, action

    def open_cards(self) -> PokerHole:
        assert self.hole is not None
        return self.hole

    def cash(self, cash_size: float):
        assert self.stack >= 0 and cash_size >= 0, (self.stack, cash_size)
        self.stack += cash_size

    def join_tournament(
        self,
        buy_in: float,
        max_num_buy_ins: int,
        time_bank: Optional[float] = None,
    ):
        """ """
        self.left_num_buy_ins = max_num_buy_ins
        self.time_bank = time_bank
        self.try_buy_in(buy_in, buy_in)

    def try_buy_in(self, min_buy_in: float, max_buy_in: float):
        assert np.isclose(self.stack, 0)
        assert min_buy_in > 0 and max_buy_in > 0 and max_buy_in >= min_buy_in
        if self.left_num_buy_ins is not None and self.left_num_buy_ins == 0:
            # Used all number of buy ins for tounament
            self.status = PlayerStatus.ELIMINATED
        elif min_buy_in > self.bank_roll:
            # Cannot buy in if not enough bank roll
            self.status = PlayerStatus.ELIMINATED
        else:
            # TODO: Simply buy in Max possible buy-in amount currently
            # TODO: Player status should be sitting out unless player wants to rejoin
            self.status = PlayerStatus.WAITING_HAND
            buy_in = min(max_buy_in, self.bank_roll)
            self.bank_roll = self.bank_roll - buy_in
            if self.left_num_buy_ins is not None:
                self.left_num_buy_ins = self.left_num_buy_ins - 1
            self.stack = buy_in

    def blind(self, small_blind: float, big_blind: float) -> float:
        assert self.stack > 0
        assert (
            self.position == PlayerPosition.SMALLBLIND
            or self.position == PlayerPosition.BIGBLIND
        )
        big = self.position == PlayerPosition.BIGBLIND
        blind = big_blind if big else small_blind
        if self.stack <= small_blind:
            self.status = PlayerStatus.CALL
        else:
            self.status = PlayerStatus.RAISE
        blind_val = min(self.stack, blind)
        self.stack = self.stack - blind_val
        self.stage_bet += blind_val
        return blind_val

    def straddle(
        self, player_stacks: List[float], player_idx: int, big_blind: float
    ) -> bool:
        if self.stack < 2 * big_blind:
            straddle = False
        else:
            straddle = self.action_agent.straddle(player_stacks, player_idx, big_blind)
        if straddle:
            self.status = PlayerStatus.RAISE
            self.stack = self.stack - 2 * big_blind
            self.stage_bet += 2 * big_blind
        return straddle

    def net_profit(self):
        return self.stack + self.bank_roll - self.start_bank_roll

    def leave_game(self):
        self.bank_roll += self.stack
        self.reset()

    def join_next_hand(self):
        self.status = PlayerStatus.WAITING_HAND

    def is_sitting_out(self):
        return self.status == PlayerStatus.SITTING_OUT

    def is_all_in(self):
        return np.isclose(self.stack, 0) and (
            self.status == PlayerStatus.CALL or self.status == PlayerStatus.RAISE
        )

    def is_eliminated(self):
        eliminated = False
        if self.status == PlayerStatus.ELIMINATED:
            assert self.left_num_buy_ins is None or np.isclose(self.left_num_buy_ins, 0)
            assert np.isclose(self.stack, 0), self.stack
            eliminated = True
        return eliminated

    def is_active(self):
        """
        Player is at an actionable state. (Can Raise / Bet)
        """
        return (
            self.status not in [PlayerStatus.FOLD, PlayerStatus.WAITING_HAND]
            and not self.is_eliminated()
            and not self.is_sitting_out()
            and not self.is_all_in()
        )

    def is_alive(self):
        """
        Player is still participating in the current hand (but can be all-in)
        """
        return (
            self.status not in [PlayerStatus.FOLD, PlayerStatus.WAITING_HAND]
            and not self.is_eliminated()
            and not self.is_sitting_out()
        )

    def is_joining(self):
        """
        Player is in a state to receive a new hand.
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
        return f"{self.name} ({self.position}): ${self.stack:.02f}"

    def __repr__(self):
        return self.__str__()
