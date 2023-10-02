from enum import Enum


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


class PokerSuit(Enum):
    ClOVER = 1
    DIAMOND = 2
    HEART = 3
    SPADE = 4


SUIT_STRING_TO_SUIT = {
    "c": PokerSuit.ClOVER,
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
