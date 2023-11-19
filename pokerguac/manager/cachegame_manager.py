import math

from ..poker import PokerTable, PokerPlayer
from typing import List, Dict, TypedDict, OrderedDict
from ..poker.components.constants import MAX_NUM_PLAYERS
from .poker_manager import PokerGameManager, GameConfig
from ..config import TableGameConfig, CacheGameConfig


class CacheGameStatus(TypedDict):
    num_players: int
    num_tables: int
    waitlist: Dict[TableGameConfig, List[PokerPlayer]]


class CacheGameManager(PokerGameManager):
    tables: List[PokerTable]
    player_table_assignments: Dict[PokerPlayer, PokerTable]
    waitlist: Dict[TableGameConfig, List[PokerPlayer]]
    cfg: CacheGameConfig

    def __init__(self, cfg: GameConfig):
        assert isinstance(cfg, CacheGameConfig)
        super().__init__(cfg)

    def needs_rebalance(self) -> bool:
        return super().needs_rebalance()

    def rebalance_tables(self) -> None:
        return super().rebalance_tables()

    def update_blind(self) -> None:
        pass

    def update_waitlist(self) -> None:
        pass

    def compute_prize_pool(self) -> None:
        pass

    def get_game_status(self) -> Dict[TableGameConfig, CacheGameStatus]:
        cache_game_status_dict = OrderedDict()
        for table in self.tables:
            game_status = cache_game_status_dict.get(
                table.cfg,
                CacheGameStatus(num_players=0, num_tables=0, waitlist=self.waitlist),
            )
            game_status["num_tables"] += 1
            for player in table.players:
                if player is not None:
                    game_status["num_players"] += 1

        return cache_game_status_dict
