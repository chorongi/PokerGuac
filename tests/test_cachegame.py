import unittest
import logging
import numpy as np
from tqdm import trange

from pokerguac.poker import ALL_AGENT_TYPES
from pokerguac.poker.components.constants import MAX_NUM_PLAYERS, MIN_NUM_PLAYERS
from pokerguac.poker_engine import poker_cache_game_init


REPORT_PERIOD = 25
NUM_TEST_EPOCHS = 100
MAX_ITERS = 1000
TEST_PERIOD = 10


class TestCacheGame(unittest.TestCase):
    def setUp(self):
        self.test_epochs = NUM_TEST_EPOCHS
        self.report_period = REPORT_PERIOD
        self.max_iters = MAX_ITERS
        self.test_period = TEST_PERIOD
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

    def test_cache_game_play(self):
        # Using large blinds just for testing purposes
        big_blind = 3
        small_blind = 1
        min_buy_in = 100
        max_buy_in = 300
        player_bank_rolls = (
            np.random.uniform(low=1, high=3, size=len(self.player_names)) * max_buy_in
        ).tolist()

        for epoch in trange(self.test_epochs):
            iter = 1
            num_players = np.random.randint(MIN_NUM_PLAYERS, MAX_NUM_PLAYERS + 1)
            action_agent_types = list(
                np.random.choice(ALL_AGENT_TYPES, num_players, replace=True)
            )
            table, players = poker_cache_game_init(
                self.player_names[:num_players],
                player_bank_rolls[:num_players],
                action_agent_types,
                num_players,
                small_blind,
                big_blind,
                min_buy_in,
                max_buy_in,
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
                if iter > self.max_iters:
                    break
                table.play_hand()
                if iter % self.test_period == 0:
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
                    "################ Poker Cache Game Final Results ################"
                )
                logging.info(table.player_rankings_report()[1])


if __name__ == "__main__":
    unittest.main()
