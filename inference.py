import numpy as np

from pokerguac.poker import PokerPlayer
from pokerguac.poker import build_action_agent
from pokerguac import PokerTable

num_players = 9
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
min_buy_in = 100
max_buy_in = 300
num_buy_in = 0
report_period = 100

players = [
    PokerPlayer(
        player_names[i],
        np.random.uniform(min_buy_in, max_buy_in),
        num_buy_ins=num_buy_in,
        action_agent=build_action_agent("simple"),
    )
    for i in range(num_players)
]
table = PokerTable(
    num_players=num_players,
    big_blind=big_blind,
    small_blind=small_blind,
    min_buy_in=min_buy_in,
    max_buy_in=max_buy_in,
)
for player in players:
    table.seat_player(player)

before_total_pot = 0
for player in players:
    before_total_pot += player.stack

iter = 0
while not table.finished():
    table.play_hand()
    if iter % report_period == 0:
        print("-------------------------------")
        print(table.player_rankings_report())
        after_total_pot = 0
        for player in players:
            after_total_pot += player.stack
        assert np.allclose(before_total_pot, after_total_pot), (
            before_total_pot,
            after_total_pot,
        )
    iter += 1
