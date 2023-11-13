from ..poker import PokerTable, PokerPlayer
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from ..poker.components.constants import MIN_NUM_PLAYERS


class PokerGameManager(ABC):
    tables: List[PokerTable]
    players: List[PokerPlayer]
    player_table_assignments: Dict[PokerPlayer, PokerTable]
    waitlist: List[PokerPlayer]
    timer: Optional[float]

    def __init__(self):
        self.tables = []
        self.players = []
        self.player_table_assignments = {}
        self.waitlist = []

    def register_player(self, player: PokerPlayer):
        self.waitlist.append(player)

    def try_seat_player(self):
        success = True
        while success and self.waitlist:
            success = False
            player = self.waitlist[0]
            for table in sorted(
                self.tables, key=lambda x: x.get_num_empty_seats(), reverse=True
            ):
                success = table.seat_player(player)
                if success:
                    self.waitlist.pop(0)
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
                self.waitlist = remaining_players + self.waitlist
            elif table.paused():
                table.active = False
            else:
                continue

    @abstractmethod
    def rebalance_tables(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_blind(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_game_status(self) -> List[str]:
        raise NotImplementedError
