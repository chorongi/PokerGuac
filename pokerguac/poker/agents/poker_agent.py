import numpy as np

from abc import ABC, abstractmethod
from typing import Tuple, List, Dict
from ..components.card import PokerBoard
from ..components import PlayerAction, PokerStage, PlayerPosition


class PokerAgent(ABC):
    name: str

    @abstractmethod
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
        raise NotImplementedError

    def straddle(
        self, player_stacks: List[float], player_idx: int, big_blind: float
    ) -> bool:
        return False

    def is_legal_bet(self, bet: float) -> bool:
        return True
