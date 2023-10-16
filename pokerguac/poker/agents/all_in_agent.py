import numpy as np
from typing import Tuple, List

from .poker_agent import PokerAgent
from ..components import PlayerAction, PokerBoard


class AllInAgent(PokerAgent):
    name: str = "all-in"

    # Agent that plays loose passive
    def action(
        self,
        board: PokerBoard,
        per_player_bet: List[float],
        per_player_action: List[List[Tuple[PlayerAction, float]]],
        big_blind: float,
        button_pos: int,
        player_pos: int,
        player_stack: float,
    ) -> Tuple[float, PlayerAction]:
        min_bet = np.max(per_player_bet) - per_player_bet[player_pos]
        player_bet = player_stack
        if min_bet >= player_bet:
            action = PlayerAction.CALL
        else:
            action = PlayerAction.RAISE
        assert self.is_legal_bet(player_bet)
        return player_bet, action
