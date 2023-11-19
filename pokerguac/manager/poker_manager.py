from ..poker import PokerTable, PokerPlayer
from typing import List, Dict, Union, Tuple, Optional, TypedDict
from abc import ABC, abstractmethod
from ..poker.components.constants import MIN_NUM_PLAYERS
from ..poker import PokerGameType
from .blind_manager import BlindManager, BlindManagerType
from ..config import TableGameConfig, CacheGameConfig, TournamentConfig, GameConfig


class PokerGameManager(ABC):
    tables: List[PokerTable]
    num_entries: int
    player_table_assignments: Dict[PokerPlayer, PokerTable]
    waitlist: Dict[TableGameConfig, List[PokerPlayer]]
    cfg: GameConfig

    def __init__(self, cfg: GameConfig):
        self.tables = []
        self.players = []
        self.player_table_assignments = {}
        self.cfg = cfg
        self.waitlist = {table_cfg: [] for table_cfg in cfg["table_configs"]}

    def register_player(self, player: PokerPlayer, table_cfg: TableGameConfig):
        self.waitlist[table_cfg].append(player)
        min_buy_in, max_buy_in = table_cfg["min_buy_in"], table_cfg["max_buy_in"]
        player.try_buy_in(min_buy_in, max_buy_in)
        self.compute_prize_pool()

    def try_seat_player(self):
        success = True
        self.update_waitlist()
        while success and self.waitlist:
            success = False
            for table_cfg in self.waitlist:
                player = self.waitlist[table_cfg][0]
                for table in sorted(
                    self.tables, key=lambda x: x.get_num_empty_seats(), reverse=True
                ):
                    if table.cfg != table_cfg:
                        continue
                    else:
                        success = table.seat_player(player)
                        if success:
                            self.waitlist[table_cfg].pop(0)
                            self.num_entries += 1
                            break

    def update_table_status(self):
        """
        Activate tables that have enough active players and
        Break tables that do not have enough active players
        """
        for table in self.tables:
            if table.can_activate():
                table.activate_table()
            elif table.finished():
                remaining_players = table.break_table()
                self.waitlist[table.cfg] = remaining_players + self.waitlist[table.cfg]
            elif table.paused():
                table.active = False
            else:
                continue

    @abstractmethod
    def compute_prize_pool(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_waitlist(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def needs_rebalance(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def rebalance_tables(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_blind(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_game_status(self) -> Dict:
        """
        Returns
        -------
        A dictionary that contains info about current status of game
        """
        raise NotImplementedError
