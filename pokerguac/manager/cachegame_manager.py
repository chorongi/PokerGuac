import math

from ..poker import PokerTable, PokerPlayer
from typing import List, Dict
from ..poker.components.constants import MAX_NUM_PLAYERS
from .poker_manager import PokerGameManager


class CacheGameManager(PokerGameManager):
    tables: List[PokerTable]
    players: List[PokerPlayer]
    player_table_assignments: Dict[PokerPlayer, PokerTable]
    waitlist: List[PokerPlayer]

    def __init__(self):
        self.tables = []
        self.players = []
        self.player_table_assignments = {}
        self.waitlist = []

    def rebalance_tables(self) -> None:
        return super().rebalance_tables()

    def update_blind(self) -> None:
        pass

    def get_game_status(self) -> List[str]:
        return super().get_game_status()
