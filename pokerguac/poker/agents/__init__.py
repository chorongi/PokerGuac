from abc import ABC, abstractmethod
from typing import Tuple
from enum import Enum


class PlayerAction(Enum):
    WAITING = 0
    CALL = 1
    RAISE = 2
    FOLD = 3
    SMALL_BLIND = 4
    BIG_BLIND = 5
    STRADDLE = 6


class PokerAgent(ABC):
    @abstractmethod
    def action(self) -> Tuple[float, PlayerAction]:
        raise NotImplementedError
