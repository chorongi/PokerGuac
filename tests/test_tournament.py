import unittest
import logging
import numpy as np
from tqdm import trange

from pokerguac.poker import ALL_AGENT_TYPES
from pokerguac.poker.components.constants import MAX_NUM_PLAYERS, MIN_NUM_PLAYERS
from pokerguac.poker_engine import poker_tournament_init

REPORT_PERIOD = 25
NUM_TEST_EPOCHS = 100
BLIND_UPDATE_PERIOD = 50
TEST_PERIOD = 10


class TestTournament(unittest.TestCase):
    def setUp(self):
        self.test_epochs = NUM_TEST_EPOCHS
        self.report_period = REPORT_PERIOD
        self.blind_update_period = BLIND_UPDATE_PERIOD
        self.player_names = [
            "Alex",
            "Jenny",
            "Shane",
            "Jun",
            "Steve",
            "Jason",
            "Chris",
            "Sung",
            "Andrew",
        ]

    def test_tournament_play(self):
        big_blind = 3
        small_blind = 1
        num_buy_ins = 3
        tournament_buy_in = 300

        for epoch in trange(self.test_epochs):
            iter = 1
            level = 1
            num_players = np.random.randint(MIN_NUM_PLAYERS, MAX_NUM_PLAYERS + 1)
            action_agent_types = list(
                np.random.choice(ALL_AGENT_TYPES, num_players, replace=True)
            )
            table, players = poker_tournament_init(
                self.player_names[:num_players],
                action_agent_types,
                num_players,
                small_blind,
                big_blind,
                num_buy_ins,
                tournament_buy_in,
            )

            before_total_bank_roll = 0
            for player in players:
                before_total_bank_roll += player.bank_roll + player.stack

            # Prepare player for play
            for player in players:
                player.join_next_hand()

            # Start game
            table.activate_table()

            while not table.finished():
                table.play_hand()
                if iter % self.blind_update_period == 0:
                    table.update_blind(small_blind * level, big_blind * level)
                    level += 1

                # Do a simple total bank roll preservation check
                after_total_bank_roll = 0
                for player in players:
                    after_total_bank_roll += player.bank_roll + player.stack
                self.assertTrue(
                    np.allclose(before_total_bank_roll, after_total_bank_roll),
                    (before_total_bank_roll, after_total_bank_roll),
                )
                table_net_profit = 0
                for player in players:
                    table_net_profit += player.net_profit()
                # Check if zero-sum game
                self.assertTrue(np.isclose(table_net_profit, 0))
                iter += 1

            if epoch % self.report_period == 0:
                logging.info(
                    "################ Poker Tournament Final Results ################"
                )
                logging.info(table.player_rankings_report()[1])


if __name__ == "__main__":
    unittest.main()
