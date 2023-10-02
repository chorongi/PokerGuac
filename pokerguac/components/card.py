from typing import Tuple
from . import NUMBER_STRING_TO_INT, SUIT_STRING_TO_SUIT, PokerSuit


class PokerCard:
    _name: int
    _orig_number: str
    _suit: PokerSuit

    def __init__(self, number: str, suit: str):
        assert number in NUMBER_STRING_TO_INT and suit in SUIT_STRING_TO_SUIT
        self._orig_number = number
        self._number = NUMBER_STRING_TO_INT[number]
        self._suit = SUIT_STRING_TO_SUIT[suit]

    def __lt__(self, other) -> bool:
        if self.__class__ is other.__class__:
            return self._number < other._number
        return NotImplemented

    def __sub__(self, other) -> int:
        if self.__class__ is other.__class__:
            return self._number - other._number
        return NotImplemented

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__ and self._number == other._number

    def __hash__(self):
        return self._number

    def __str__(self):
        return f"{self._orig_number}{self._suit}"

    def has_suit(self, suit: PokerSuit):
        return self._suit == suit

    def suit_eq(self, other):
        return self._suit == other._suit


PokerBoard = Tuple[PokerCard, PokerCard, PokerCard, PokerCard, PokerCard]
PokerHand = Tuple[PokerCard, PokerCard]
