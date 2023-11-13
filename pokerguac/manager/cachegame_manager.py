from ..poker import PokerTable, PokerPlayer
from typing import List, Dict
from ..poker.components.constants import MIN_NUM_PLAYERS


class CacheGameManager:
    tables: List[PokerTable]
    players: List[PokerPlayer]
    player_table_assignments: Dict[PokerPlayer, PokerTable]
    waitlist: List[PokerPlayer]

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
            for table in self.tables:
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
