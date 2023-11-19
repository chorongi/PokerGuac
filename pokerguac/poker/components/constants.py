from enum import Enum
from typing import Mapping

# fmt: off
POKER_CARD_DECK = [
    "ac", "ad", "ah", "as",
    "2c", "2d", "2h", "2s",
    "3c", "3d", "3h", "3s",
    "4c", "4d", "4h", "4s",
    "5c", "5d", "5h", "5s",
    "6c", "6d", "6h", "6s",
    "7c", "7d", "7h", "7s",
    "8c", "8d", "8h", "8s",
    "9c", "9d", "9h", "9s",
    "tc", "td", "th", "ts",
    "jc", "jd", "jh", "js",
    "kc", "kd", "kh", "ks",
    "qc", "qd", "qh", "qs",
]
# fmt: on

INVALID_NAMES = ["empty", "", "\n"]


class PrintableEnum(Enum):
    def __str__(self):
        return self.name


class PokerSuit(PrintableEnum):
    CLOVER = 1
    DIAMOND = 2
    HEART = 3
    SPADE = 4


class PlayerAction(PrintableEnum):
    CALL = 0
    RAISE = 1
    FOLD = 2
    SMALL_BLIND = 3
    BIG_BLIND = 4
    STRADDLE = 5


class PlayerStatus(PrintableEnum):
    CALL = 0
    RAISE = 1
    FOLD = 2
    WAITING_TURN = 3  # Waiting to make action on current stage
    WAITING_HAND = 4  # Waiting to join next hand
    SITTING_OUT = 5  # Sitting out and to stay away from game
    ELIMINATED = 6  # Eliminated from tournament


class PlayerPosition(PrintableEnum):
    SMALLBLIND = 0
    BIGBLIND = 1
    UTG = 2
    UTG1 = 3
    UTG2 = 4
    LOWJACK = 5
    HIGHJACK = 6
    CUTOFF = 7
    BUTTON = 8

    def __str__(self):
        enum_to_str: Mapping[str, str] = {
            "SMALLBLIND": "SB",
            "BIGBLIND": "BB",
            "UTG": "UTG",
            "UTG1": "UTG1",
            "UTG2": "UTG2",
            "LOWJACK": "LJ",
            "HIGHJACK": "HJ",
            "CUTOFF": "CO",
            "BUTTON": "B",
        }
        return enum_to_str[self.name]


class PlayerType(PrintableEnum):
    PERSON = 0
    AI = 1


class PokerStage(PrintableEnum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3

    def next(self):
        return PokerStage((self.value + 1) % len(list(self.__class__)))


class PokerTableState(PrintableEnum):
    BLIND = 0
    STRADDLE = 1
    DRAW_CARDS = 2
    PLAYER_ACTION = 3
    END_STAGE = 4
    END_ROUND = 5
    MOVE_BUTTON = 6
    PAUSED = 7


ALL_POKER_STAGES = [
    PokerStage.PREFLOP,
    PokerStage.FLOP,
    PokerStage.TURN,
    PokerStage.RIVER,
]

SUIT_STRING_TO_SUIT = {
    "c": PokerSuit.CLOVER,
    "d": PokerSuit.DIAMOND,
    "h": PokerSuit.HEART,
    "s": PokerSuit.SPADE,
}

NUMBER_STRING_TO_INT = {
    "a": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "t": 10,
    "j": 11,
    "q": 12,
    "k": 13,
}

MAX_NUM_PLAYERS = 9
MIN_NUM_PLAYERS = 2
BOARD_NUM_CARDS = 5
NUM_FLOP_CARDS = 3
NUM_TURN_CARDS = 1
NUM_RIVER_CARDS = 1
HOLDEM_NUM_PLAYER_CARDS = 2
MIN_BLIND_LEVELS = 5

NUM_PLAYERS_TO_POSITIONS = {
    2: [PlayerPosition.SMALLBLIND, PlayerPosition.BIGBLIND],
    3: [PlayerPosition.SMALLBLIND, PlayerPosition.BIGBLIND, PlayerPosition.BUTTON],
    4: [
        PlayerPosition.SMALLBLIND,
        PlayerPosition.BIGBLIND,
        PlayerPosition.UTG,
        PlayerPosition.BUTTON,
    ],
    5: [
        PlayerPosition.SMALLBLIND,
        PlayerPosition.BIGBLIND,
        PlayerPosition.UTG,
        PlayerPosition.CUTOFF,
        PlayerPosition.BUTTON,
    ],
    6: [
        PlayerPosition.SMALLBLIND,
        PlayerPosition.BIGBLIND,
        PlayerPosition.UTG,
        PlayerPosition.UTG1,
        PlayerPosition.CUTOFF,
        PlayerPosition.BUTTON,
    ],
    7: [
        PlayerPosition.SMALLBLIND,
        PlayerPosition.BIGBLIND,
        PlayerPosition.UTG,
        PlayerPosition.UTG1,
        PlayerPosition.UTG2,
        PlayerPosition.CUTOFF,
        PlayerPosition.BUTTON,
    ],
    8: [
        PlayerPosition.SMALLBLIND,
        PlayerPosition.BIGBLIND,
        PlayerPosition.UTG,
        PlayerPosition.UTG1,
        PlayerPosition.UTG2,
        PlayerPosition.HIGHJACK,
        PlayerPosition.CUTOFF,
        PlayerPosition.BUTTON,
    ],
    9: [
        PlayerPosition.SMALLBLIND,
        PlayerPosition.BIGBLIND,
        PlayerPosition.UTG,
        PlayerPosition.UTG1,
        PlayerPosition.UTG2,
        PlayerPosition.LOWJACK,
        PlayerPosition.HIGHJACK,
        PlayerPosition.CUTOFF,
        PlayerPosition.BUTTON,
    ],
}
