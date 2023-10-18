from typing import Tuple, Optional, List
from .constants import NUMBER_STRING_TO_INT, SUIT_STRING_TO_SUIT, PokerSuit


__all__ = ["PokerCard", "PokerBoard", "PokerHand", "PokerHole"]


class PokerCard:
    """
    PokerCard class for Texas Holdem Poker game
    operations like __eq__, __hash__ use only "number" component of card
    for usage in cardops for hand rank computation.
    (i.e. PokerCard.from_symbol('as') == PokerCard.from_symbol('ad'))
    """

    _name: str
    _number: int
    _suit: PokerSuit

    def __init__(self, number: str, suit: str):
        assert number in NUMBER_STRING_TO_INT and suit in SUIT_STRING_TO_SUIT
        self._name = f"{number}{suit}"
        self._number = NUMBER_STRING_TO_INT[number]
        self._suit = SUIT_STRING_TO_SUIT[suit]

    @classmethod
    def from_symbol(cls, symbol: str):
        assert (
            len(symbol) == 2
        ), f"{symbol} is invalid. Valid symbols are [as, kd, 2h, 3c, ...]"
        number = symbol[0].lower()
        suit = symbol[1].lower()
        return cls(number, suit)

    def equal(self, other) -> bool:
        return (
            self.__class__ == other.__class__
            and self._number == other._number
            and self._suit == other._suit
        )

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
        return self._name

    def __repr__(self):
        return self.__str__()

    def has_suit(self, suit: PokerSuit):
        return self._suit == suit

    def suit_eq(self, other):
        return self._suit == other._suit


PokerBoard = List[Optional[PokerCard]]
PokerHand = Tuple[PokerCard, PokerCard, PokerCard, PokerCard, PokerCard]
PokerHole = Tuple[PokerCard, PokerCard]
