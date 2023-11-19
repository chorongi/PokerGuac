from ..poker import (
    PokerTable,
    PokerPlayer,
    MIN_NUM_PLAYERS,
    MAX_NUM_PLAYERS,
    MIN_BLIND_LEVELS,
)
from typing import List, Dict
from .poker_manager import PokerGameManager
from .blind_manager import BlindManager

__all__ = ["TournamentManager"]


class TournamentManager(PokerGameManager):
    tables: List[PokerTable]
    players: List[PokerPlayer]
    player_table_assignments: Dict[PokerPlayer, PokerTable]
    waitlist: List[PokerPlayer]
    blind_manager: BlindManager

    def __init__(
        self,
    ):
        self.tables = []
        self.players = []
        self.player_table_assignments = {}
        self.waitlist = []
