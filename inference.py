import numpy as np
from tqdm import trange
from typing import List
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
from pokerguac.poker import ALL_AGENT_TYPES, AgentType

big_blind = 3
small_blind = 1
min_buy_in = 100
max_buy_in = 300
num_buy_in = 1

REPORT_PERIOD = 100
BLIND_UPDATE_PERIOD = 100
NUM_TEST_EPOCHS = 10000


def poker_init(agent_types: List[AgentType]):
    players = [
        PokerPlayer(
            player_names[i],
            num_buy_ins=num_buy_in,
            action_agent=build_action_agent(agent_types[i]),
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
        player.buy_in(np.random.uniform(min_buy_in, max_buy_in))

    for player in players:
        table.seat_player(player)
    return table, players


for epoch in trange(NUM_TEST_EPOCHS):
    iter = 0
    action_agent_types = np.random.choice(ALL_AGENT_TYPES, num_players, replace=True)
    table, players = poker_init(action_agent_types)
    before_total_pot = 0
    for player in players:
        before_total_pot += player.stack
    while not table.finished():
        table.play_hand()
        if iter % BLIND_UPDATE_PERIOD == 0:
            # Do a simple total pot preservation check
            after_total_pot = 0
            for player in players:
                after_total_pot += player.stack
            assert np.allclose(before_total_pot, after_total_pot), (
                before_total_pot,
                after_total_pot,
            )
            table.update_blind(table.small_blind * 1.1, table.big_blind * 1.1)
        iter += 1

    if epoch % REPORT_PERIOD == 0:
        print("################ Poker Final Results ################")
        print(table.player_rankings_report()[1])
