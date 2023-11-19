from abc import ABC, abstractmethod
import math
import time
from typing import Literal, Tuple
from ..poker import (
    MIN_NUM_PLAYERS,
    MAX_NUM_PLAYERS,
    MIN_BLIND_LEVELS,
)
from ..config import BlindManagerType, TournamentConfig

__all__ = [
    "BlindManager",
    "TimeBlindManager",
    "HandBlindManager",
    "build_blind_manager",
    "BlindManagerType",
]


class BlindManager(ABC):
    def __init__(
        self,
        target_duration: float,
        target_num_entries: int,
        blind_update_period: float,
        base_starting_stack: int = 5000,
        start_effective_stack: int = 100,
    ):
        """
        Args
        ----
        target_duration (float): target duration of tournament
        target_num_entries (int): target number of entries
        blind_update_period (float): blind update period
        base_starting_stack (int): Base unit for starting stack. (default = 5000)
        start_effective_stack (int): Starting stack (in BBs) that participants start with on entry. (default 100 BB)

        minimum number of blind levels is 10
        minimum start effective stack is 25 BB and max is 250 BB
        minimum number of target entries is 2
        """
        assert target_duration / blind_update_period >= MIN_BLIND_LEVELS
        assert start_effective_stack >= 25 and start_effective_stack <= 250
        assert base_starting_stack > 0
        assert target_num_entries >= MIN_NUM_PLAYERS
        self.starting_stack = base_starting_stack * int(math.ceil(target_duration / 8))
        self.start_effective_stack = start_effective_stack
        self.target_duration = target_duration
        self.target_num_entries = target_num_entries
        self.blind_period = blind_update_period
        self.reset()

    @abstractmethod
    def start(self):
        raise NotImplementedError

    @abstractmethod
    def pause(self):
        raise NotImplementedError

    @abstractmethod
    def resume(self):
        raise NotImplementedError

    @abstractmethod
    def try_update_blind(self, game_progress: float):
        """
        Args
        ----
        game_progress (float):
            indicator of tournament progress. e.g. hand number, current time
        """
        raise NotImplementedError

    @abstractmethod
    def until_next_blind(self, game_progress: float) -> float:
        """
        Returns
        -------
        time or number of hands until next blind update
        """
        raise NotImplementedError

    def reset(self):
        self.blind_start = 0
        self.curr_level = 1
        self.init_blind()

    def init_blind(self):
        blind = self.starting_stack / self.start_effective_stack
        num_digits = max(int(math.floor(math.log10(self.blind))) - 1, 0)
        start_blind = round(blind / (10**num_digits)) * (10**num_digits)
        num_target_levels = math.ceil(self.target_duration / self.blind_period)
        # Rule of thumb is that tournament will end when BB = 7% of chips in play
        target_final_blind = self.starting_stack * self.target_num_entries * 0.07
        # start_blind * (self.ratio ** self.num_total_levels) = final_blind
        self.ratio = math.exp(
            math.log(target_final_blind / start_blind) / num_target_levels
        )
        self.blind = start_blind

    def update_blind(self):
        num_digits = max(int(math.floor(math.log10(self.blind))) - 1, 0)
        self.blind = round(self.blind * self.ratio / (10**num_digits)) * (
            10**num_digits
        )

    def next_blind(self) -> Tuple[float, float]:
        num_digits = max(int(math.floor(math.log10(self.blind))) - 1, 0)
        blind = round(self.blind * self.ratio / (10**num_digits)) * (10**num_digits)
        return blind, blind // 2


class HandBlindManager(BlindManager):
    """
    Blind Managerer that handles blind updates with progression of hand
    Usually preferred to used for final table
    """

    def __init__(
        self,
        target_duration: float,
        target_num_entries: int,
        blind_update_period: float,
        base_starting_stack: int = 5000,
        start_effective_stack: int = 100,
    ):
        """
        Args
        ----
        target_duration (float): target duration time of tournament in hands
        target_num_entries (int): target number of entries
        blind_update_period (float): blind update period in hands
        base_starting_stack (int): Base unit for starting stack. (default = 5000)
        start_effective_stack (int): Starting stack (in BBs) that participants start with on entry. (default 100 BB)

        minimum number of blind levels is 10
        minimum start effective stack is 25 BB and max is 250 BB
        minimum number of target entries is 2
        """
        assert target_duration >= 10 and target_duration == int(target_duration)
        assert blind_update_period >= 1 and blind_update_period == int(
            blind_update_period
        )
        super().__init__(
            target_duration,
            target_num_entries,
            blind_update_period,
            base_starting_stack,
            start_effective_stack,
        )

    def start(self):
        self.blind_start = 1

    def pause(self):
        pass

    def resume(self):
        pass

    def try_update_blind(self, game_progress: float):
        """
        Args
        ----
        game_progress (float):
            Current hand number of tournament.
        """
        assert game_progress == int(game_progress)
        assert game_progress >= self.blind_start
        if game_progress - self.blind_start >= self.blind_period:
            self.update_blind()
            self.curr_level += 1
            self.blind_start = game_progress

    def until_next_blind(self, game_progress: float) -> float:
        return self.blind_start + self.blind_period - game_progress


class TimeBlindManager(BlindManager):
    def __init__(
        self,
        target_duration: float,
        target_num_entries: int,
        blind_update_period: float,
        base_starting_stack: int = 5000,
        start_effective_stack: int = 100,
    ):
        """
        Args
        ----
        target_duration (float): target duration time of tournament in hours
        target_num_entries (int): target number of entries
        blind_update_period (float): blind update period in hours
        base_starting_stack (int): Base unit for starting stack. (default = 5000)
        start_effective_stack (int): Starting stack (in BBs) that participants start with on entry. (default 100 BB)

        minimum number of blind levels is 10
        minimum start effective stack is 25 BB and max is 250 BB
        minimum number of target entries is 2
        """
        super().__init__(
            target_duration,
            target_num_entries,
            blind_update_period,
            base_starting_stack,
            start_effective_stack,
        )

    def start(self):
        self.blind_start = time.time()

    def pause(self):
        self.pause_time = time.time()

    def resume(self):
        self.blind_start += time.time() - self.pause_time
        self.pause_time = 0

    def try_update_blind(self, game_progress: float):
        """
        Args
        ----
        game_progress (float):
            Current time of tournament in seconds
        """
        assert game_progress >= self.blind_start
        if (game_progress - self.blind_start) / 3600 >= self.blind_period:
            self.update_blind()
            self.curr_level += 1
            self.blind_start = game_progress

    def until_next_blind(self, game_progress: float) -> float:
        return self.blind_start / 3600 + self.blind_period - game_progress / 3600


def build_blind_manager(cfg: TournamentConfig) -> BlindManager:
    blind_manager_type = cfg["blind_manager_type"]
    if blind_manager_type == "hand":
        blind_manager_cls = HandBlindManager
    elif blind_manager_type == "time":
        blind_manager_cls = TimeBlindManager
    else:
        raise ValueError(f"Unsupported blind manager type {blind_manager_type}")

    return blind_manager_cls(
        target_duration=cfg["target_duration"],
        target_num_entries=cfg["target_num_entries"],
        blind_update_period=cfg["blind_update_period"],
        base_starting_stack=cfg["base_starting_stack"],
        start_effective_stack=cfg["start_effective_stack"],
    )
