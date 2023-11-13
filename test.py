import numpy as np
from tqdm import trange
from typing import List
from pokerguac.poker import PokerPlayer

from pokerguac.poker import ALL_AGENT_TYPES
from pokerguac.poker.components.constants import MAX_NUM_PLAYERS, MIN_NUM_PLAYERS
from pokerguac.poker_engine import poker_cache_game_init, poker_tournament_init


def test_cache_game_play(
    test_epochs: int, report_period: int, test_period: int, max_iters: int
):
    player_names = [
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
    # Using large blinds just for testing purposes
    big_blind = 3
    small_blind = 1
    min_buy_in = 100
    max_buy_in = 300
    player_bank_rolls = (
        np.random.uniform(low=1, high=3, size=len(player_names)) * max_buy_in
    ).tolist()

    for epoch in trange(test_epochs):
        iter = 1
        num_players = np.random.randint(MIN_NUM_PLAYERS, MAX_NUM_PLAYERS + 1)
        action_agent_types = list(
            np.random.choice(ALL_AGENT_TYPES, num_players, replace=True)
        )
        table, players = poker_cache_game_init(
            player_names[:num_players],
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
            if iter > max_iters:
                break
            table.play_hand()
            if iter % test_period == 0:
                # Do a simple total bank roll preservation check
                after_total_bank_roll = 0
                for player in players:
                    after_total_bank_roll += player.bank_roll + player.stack
                assert np.allclose(before_total_bank_roll, after_total_bank_roll), (
                    before_total_bank_roll,
                    after_total_bank_roll,
                )
                table_net_profit = 0
                for player in players:
                    table_net_profit += player.net_profit()
                # Check if zero-sum game
                assert np.isclose(table_net_profit, 0)
            iter += 1

        if epoch % report_period == 0:
            print("################ Poker Cache Game Final Results ################")
            print(table.player_rankings_report()[1])


def test_tournament_play(
    test_epochs: int, report_period: int, test_period: int, blind_update_period: int
):
    player_names = [
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
    big_blind = 3
    small_blind = 1
    num_buy_ins = 3
    tournament_buy_in = 300

    for epoch in trange(test_epochs):
        iter = 1
        level = 1
        num_players = np.random.randint(MIN_NUM_PLAYERS, MAX_NUM_PLAYERS + 1)
        action_agent_types = list(
            np.random.choice(ALL_AGENT_TYPES, num_players, replace=True)
        )
        table, players = poker_tournament_init(
            player_names[:num_players],
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
            if iter % blind_update_period == 0:
                table.update_blind(small_blind * level, big_blind * level)
                level += 1
            if iter % test_period == 0:
                # Do a simple total bank roll preservation check
                after_total_bank_roll = 0
                for player in players:
                    after_total_bank_roll += player.bank_roll + player.stack
                assert np.allclose(before_total_bank_roll, after_total_bank_roll), (
                    before_total_bank_roll,
                    after_total_bank_roll,
                )
                table_net_profit = 0
                for player in players:
                    table_net_profit += player.net_profit()
                # Check if zero-sum game
                assert np.isclose(table_net_profit, 0)
            iter += 1

        if epoch % report_period == 0:
            print("################ Poker Tournament Final Results ################")
            print(table.player_rankings_report()[1])


REPORT_PERIOD = 25
NUM_TEST_EPOCHS = 100
BLIND_UPDATE_PERIOD = 50
MAX_ITERS = 10000
TEST_PERIOD = 10

test_cache_game_play(NUM_TEST_EPOCHS, REPORT_PERIOD, TEST_PERIOD, MAX_ITERS)
test_tournament_play(NUM_TEST_EPOCHS, REPORT_PERIOD, TEST_PERIOD, BLIND_UPDATE_PERIOD)

# test_game_simulation()
# test_board = [
#     PokerCard.from_symbol("th"),
#     PokerCard.from_symbol("4d"),
#     PokerCard.from_symbol("ah"),
#     None,
#     None,
# ]

# test_holes = [
#     (PokerCard.from_symbol("ad"), PokerCard.from_symbol("ac")),
#     (PokerCard.from_symbol("kd"), PokerCard.from_symbol("kc")),
#     (PokerCard.from_symbol("qd"), PokerCard.from_symbol("qc")),
#     (PokerCard.from_symbol("jd"), PokerCard.from_symbol("jc")),
#     (PokerCard.from_symbol("td"), PokerCard.from_symbol("tc")),
#     (PokerCard.from_symbol("ts"), PokerCard.from_symbol("th")),
#     (PokerCard.from_symbol("9s"), PokerCard.from_symbol("9h")),
#     (PokerCard.from_symbol("8s"), PokerCard.from_symbol("8h")),
#     (PokerCard.from_symbol("7d"), PokerCard.from_symbol("7c")),
#     (PokerCard.from_symbol("2d"), PokerCard.from_symbol("2c")),
#     (PokerCard.from_symbol("kd"), PokerCard.from_symbol("jc")),
#     (PokerCard.from_symbol("ks"), PokerCard.from_symbol("js")),
#     (PokerCard.from_symbol("as"), PokerCard.from_symbol("ts")),
#     (PokerCard.from_symbol("as"), PokerCard.from_symbol("th")),
#     (PokerCard.from_symbol("as"), PokerCard.from_symbol("4s")),
#     (PokerCard.from_symbol("as"), PokerCard.from_symbol("4h")),
#     (PokerCard.from_symbol("jh"), PokerCard.from_symbol("tc")),
#     (PokerCard.from_symbol("2h"), PokerCard.from_symbol("7c")),
# ]
