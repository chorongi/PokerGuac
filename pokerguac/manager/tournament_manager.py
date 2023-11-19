import time

from ..poker import (
    PokerTable,
    PokerPlayer,
    MIN_NUM_PLAYERS,
    MAX_NUM_PLAYERS,
    MIN_BLIND_LEVELS,
)
from typing import List, Dict, Optional, Tuple, TypedDict
from .prize_pool import get_prize_pool
from .poker_manager import PokerGameManager, GameConfig
from .blind_manager import (
    BlindManager,
    HandBlindManager,
    TimeBlindManager,
    build_blind_manager,
    BlindManagerType,
)
from ..config import TournamentConfig, TableGameConfig

__all__ = ["TournamentManager"]


class TournamentGameStatus(TypedDict):
    cfg: TableGameConfig
    num_entries: int
    num_players: int
    average_stack: float
    chip_leader: PokerPlayer
    next_blind: Tuple[float, float]  # Bigblind, Smallblind
    until_next_blind: Tuple[float, str]  # numeric value, unit


class TournamentManager(PokerGameManager):
    tables: List[PokerTable]
    num_entries: int
    player_table_assignments: Dict[PokerPlayer, PokerTable]
    waitlist: Dict[TableGameConfig, List[PokerPlayer]]
    blind_manager: Optional[BlindManager]
    player_ranks: List[PokerPlayer]
    cfg: TournamentConfig
    table_cfg: TableGameConfig

    def __init__(self, cfg: GameConfig):
        """
        Args
        ----
        target_duration (float): target duration of tournament
        target_num_entries (int): target number of entries
        blind_update_period (float): blind update period
        base_starting_stack (int): Base unit for starting stack. (default = 5000)
        start_effective_stack (int): Starting stack (in BBs) that participants start with on entry. (default 100 BB)
        """
        assert isinstance(cfg, TournamentConfig)
        assert len(cfg["table_configs"]) == 1
        assert (
            cfg["table_configs"][0]["min_buy_in"]
            == cfg["table_configs"][0]["max_buy_in"]
        )
        self.cfg = cfg
        self.tables = []
        self.players = []
        self.player_table_assignments = {}
        self.hand_num = 0
        self.num_entries = 0
        self.buy_in = cfg["table_configs"][0]["min_buy_in"]

        self.blind_type = self.cfg["blind_manager_type"]
        self.blind_manager = build_blind_manager(self.cfg)
        self.table_cfg = self.cfg["table_configs"][0]
        self.waitlist = {self.table_cfg: []}

    def needs_rebalance(self) -> bool:
        return super().needs_rebalance()

    def rebalance_tables(self) -> None:
        return super().rebalance_tables()

    def update_blind(self) -> None:
        if isinstance(self.blind_manager, HandBlindManager):
            game_progress = self.hand_num
        elif isinstance(self.blind_manager, TimeBlindManager):
            game_progress = time.time()
        else:
            raise ValueError("Unsupported type of blind manager")
        self.blind_manager.try_update_blind(game_progress)

    def update_waitlist(self) -> None:
        assert len(self.waitlist) == 1
        assert self.blind_manager is not None
        old_blind = list(self.waitlist.keys())[0]
        new_blind = self.blind_manager.blind
        self.waitlist[new_blind] = self.waitlist[old_blind]
        del self.waitlist[old_blind]

    def compute_prize_pool(self) -> None:
        self.prize_pool = get_prize_pool(
            self.buy_in * self.num_entries * self.cfg["prize_pool_ratio"],
            self.buy_in,
            len(self.player_ranks),
        )

    def get_game_status(self) -> TournamentGameStatus:
        total_stack = 0
        num_players = 0
        chip_leader = None
        for table in self.tables:
            for player in table.players:
                if player is not None:
                    total_stack += player.stack
                    num_players += 1
                    if chip_leader is None:
                        chip_leader = player
                    elif player.stack > chip_leader.stack:
                        chip_leader = player
        assert chip_leader is not None
        assert self.blind_manager is not None
        average_stack = total_stack / num_players
        if isinstance(self.blind_manager, HandBlindManager):
            game_progress = self.hand_num
        else:
            game_progress = time.time()
        return TournamentGameStatus(
            cfg=self.table_cfg,
            num_entries=self.num_entries,
            num_players=len(self.player_ranks),
            average_stack=average_stack,
            chip_leader=chip_leader,
            next_blind=self.blind_manager.next_blind(),
            until_next_blind=(
                self.blind_manager.until_next_blind(game_progress),
                self.blind_type,
            ),
        )
