import numpy as np
from typing import Tuple, List, Dict

from .poker_agent import PokerAgent
from ..components.card import PokerBoard
from ..components import PlayerAction, PokerStage, PlayerPosition


class SimpleAgent(PokerAgent):
    name: str = "simple"

    # Agent that simply calls
    def action(
        self,
        board: PokerBoard,
        per_player_bet: np.ndarray,
        per_player_action: Dict[PokerStage, List[List[Tuple[PlayerAction, float]]]],
        player_stacks: List[float],
        player_pos: PlayerPosition,
        player_idx: int,
        big_blind: float,
    ) -> Tuple[float, PlayerAction]:
        action = PlayerAction.CALL
        bet = np.max(per_player_bet) - per_player_bet[player_idx]
        player_stack = player_stacks[player_idx]
        if player_stack < bet:
            bet = player_stack
        assert self.is_legal_bet(bet)
        return bet, action
