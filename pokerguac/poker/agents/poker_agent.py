import numpy as np

from abc import ABC, abstractmethod
from typing import Tuple, List
from ..components.card import PokerBoard
from ..components import PlayerAction


class PokerAgent(ABC):
    name: str

    @abstractmethod
    def action(
        self,
        board: PokerBoard,
        per_player_bet: np.ndarray,
        per_player_action: List[List[PlayerAction]],
        big_blind: float,
        button_pos: int,
        player_pos: int,
        player_stack: float,
    ) -> Tuple[float, PlayerAction]:
        raise NotImplementedError

    def is_legal_bet(self, bet: float) -> bool:
        return True
