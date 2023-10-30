import numpy as np
from typing import Tuple, List, Dict

from .poker_agent import PokerAgent
from ..components import PlayerAction, PlayerPosition, PokerStage, PokerBoard


class AllInAgent(PokerAgent):
    name: str = "all-in"

    # Agent that plays loose passive
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
        min_bet = np.max(per_player_bet) - per_player_bet[player_idx]
        player_bet = player_stacks[player_idx]
        if min_bet >= player_bet:
            action = PlayerAction.CALL
        else:
            action = PlayerAction.RAISE
        assert self.is_legal_bet(player_bet)
        return player_bet, action
