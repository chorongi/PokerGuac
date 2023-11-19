from enum import Enum
from .agents import PokerAgent, build_action_agent, ALL_AGENT_TYPES, AgentType
from .poker_player import PokerPlayer
from .poker_table import PokerTable
from .components import MIN_NUM_PLAYERS, MAX_NUM_PLAYERS, MIN_BLIND_LEVELS

from typing import List, Optional


def poker_tournament_init(
    player_names: List[str],
    agent_types: List[AgentType],
    num_players: int,
    small_blind: float = 1,
    big_blind: float = 3,
    max_num_buy_ins: int = 1,
    tournament_buy_in: float = 300,
    time_bank: Optional[float] = None,
):
    """
    Currently only supports one table
    """
    assert len(player_names) == len(agent_types)
    assert big_blind >= small_blind
    assert max_num_buy_ins >= 1
    assert tournament_buy_in >= big_blind
    assert len(player_names) <= num_players
    assert num_players >= MIN_NUM_PLAYERS
    players = [
        PokerPlayer(
            player_names[i],
            action_agent=build_action_agent(agent_types[i]),
            bank_roll=max_num_buy_ins * tournament_buy_in,
        )
        for i in range(num_players)
    ]
    table = PokerTable(
        num_players=num_players,
        big_blind=big_blind,
        small_blind=small_blind,
        min_buy_in=tournament_buy_in,
        max_buy_in=tournament_buy_in,
    )

    for player in players:
        player.join_tournament(tournament_buy_in, max_num_buy_ins, time_bank=time_bank)

    for player in players:
        table.seat_player(player)
    return table, players


def poker_cache_game_init(
    player_names: List[str],
    player_bank_rolls: List[float],
    agent_types: List[AgentType],
    num_players: int,
    small_blind: float = 1,
    big_blind: float = 3,
    min_buy_in: float = 100,
    max_buy_in: float = 300,
):
    """
    Currently only supports one table
    """
    assert len(player_names) == len(agent_types)
    assert big_blind >= small_blind
    assert max_buy_in >= min_buy_in
    assert len(player_names) <= num_players
    assert num_players >= MIN_NUM_PLAYERS
    players = [
        PokerPlayer(
            player_names[i],
            action_agent=build_action_agent(agent_types[i]),
            bank_roll=player_bank_rolls[i],
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
        player.try_buy_in(min_buy_in, max_buy_in)

    for player in players:
        table.seat_player(player)
    return table, players
