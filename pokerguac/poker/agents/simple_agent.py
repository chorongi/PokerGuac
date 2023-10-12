import numpy as np
from typing import Tuple, List

from .poker_agent import PokerAgent
from ..components import PlayerAction, PokerBoard


class SimpleAgent(PokerAgent):
    name: str = "simple"

    # Agent that simply calls
    def action(
        self,
        board: PokerBoard,
        per_player_bet: List[float],
        per_player_action: List[List[PlayerAction]],
        big_blind: float,
        button_pos: int,
        player_pos: int,
        player_stack: float,
    ) -> Tuple[float, PlayerAction]:
        action = PlayerAction.CALL
        bet = np.max(per_player_bet) - per_player_bet[player_pos]
        if player_stack < bet:
            bet = player_stack
        assert self.is_legal_bet(bet)
        return bet, action
