from typing import Union, Literal, TypedDict, Mapping, Sequence
from .poker import PokerGameType

BlindManagerType = Literal["hand", "time"]


class TableGameConfig(TypedDict):
    big_blind: float
    small_blind: float
    min_buy_in: float
    max_buy_in: float
    game_type: PokerGameType


class CacheGameConfig(TypedDict):
    table_configs: Sequence[TableGameConfig]
    max_num_tables: Mapping[TableGameConfig, int]


class TournamentConfig(TypedDict):
    table_configs: Sequence[TableGameConfig]
    target_duration: float
    target_num_entries: int
    blind_update_period: float
    prize_pool_ratio: float
    base_starting_stack: int
    start_effective_stack: int
    blind_manager_type: BlindManagerType


# Default   values
# prize_pool_ratio: float = (0.5,)
# base_starting_stack: int = (5000,)
# start_effective_stack: int = (100,)
# blind_manager_type: BlindManagerType = ("time",)

GameConfig = Union[CacheGameConfig, TournamentConfig]
