from abc import ABC, abstractmethod
from typing import Tuple
from ..poker import PlayerAction


class PokerAgent(ABC):
    @abstractmethod
    def action(
        self, board, per_player_bet, per_player_action, big_blind, button, player_pos
    ) -> Tuple[float, PlayerAction]:
        raise NotImplementedError
