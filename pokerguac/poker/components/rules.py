from enum import Enum
from typing import Tuple, OrderedDict, List, cast
from abc import ABC, abstractmethod

from .card import PokerCard, PokerSuit, PokerHand, PokerBoard, PokerHole
from .card_ops import (
    ace_sort,
    get_duplicate_cards,
    get_remainder_of_pairs,
    lt_cards,
)


class HandRanking(Enum):
    ROYAL = 1
    STRAIGHTFLUSH = 2
    QUADS = 3
    FULLHOUSE = 4
    FLUSH = 5
    STRAIGHT = 6
    TRIPS = 7
    TWOPAIR = 8
    PAIR = 9
    HIGH = 10

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


__all__ = ["rank_hands"]


class HandType(ABC):
    final_hand: PokerHand
    name: HandRanking

    def __init__(self, hand: PokerHand):
        success, self.final_hand = self.check(list(hand))
        assert success, (self.final_hand, hand)

    @classmethod
    @abstractmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerHand]:
        raise NotImplementedError

    @abstractmethod
    def __lt__(self, other) -> bool:
        """
        Stronger Hand must be Larger
        """
        if self.__class__ == other.__class__:
            raise NotImplementedError
        else:
            return self.name > other.name

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__ and sorted(self.final_hand) == sorted(
            other.final_hand
        )


class Royal(HandType):
    name: HandRanking = HandRanking.ROYAL

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerHand]:
        straightflush, result = StraightFlush.check(cards)
        broadway = cls.is_broadway(list(result))
        assert len(result) == 5, result
        return straightflush and broadway, result

    @classmethod
    def is_broadway(cls, cards: List[PokerCard]) -> bool:
        ace = PokerCard("a", "s")
        king = PokerCard("k", "s")
        straight, result = Straight.check(cards)
        broadway = straight and ace in result and king in result
        return broadway

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            return False
        else:
            return self.name > other.name


class StraightFlush(HandType):
    name: HandRanking = HandRanking.STRAIGHTFLUSH

    @classmethod
    def _all_straight_flush_cards(cls, cards: List[PokerCard]) -> List[PokerCard]:
        sorted_cards = sorted(cards)
        ace = PokerCard("a", "s")
        king = PokerCard("k", "s")
        straightflush_cards = []
        for prev, curr in zip(sorted_cards[:-1], sorted_cards[1:]):
            if curr - prev == 1 and prev.suit_eq(curr):
                if prev not in straightflush_cards:
                    straightflush_cards.append(prev)
                straightflush_cards.append(curr)
            elif len(straightflush_cards) >= 5:
                break
            else:
                straightflush_cards = []

        # Handle Broadway Straight
        if king in straightflush_cards and ace in sorted_cards:
            ace_card = None
            for card in sorted_cards:
                if card == ace and card.suit_eq(straightflush_cards[0]):
                    ace_card = card
            if ace_card is not None:
                straightflush_cards.append(ace_card)

        return ace_sort(straightflush_cards, straight=True)

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerHand]:
        straightflush_cards = cls._all_straight_flush_cards(cards)
        straightflush = len(straightflush_cards) >= 5
        if straightflush:
            result = straightflush_cards[-5:]
        else:
            result = ace_sort(cards)[-5:]
        assert len(result) == 5, result
        result = cast(PokerHand, result)
        return straightflush, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            return lt_cards(self.final_hand, other.final_hand)
        else:
            return self.name > other.name


class Quads(HandType):
    name: HandRanking = HandRanking.QUADS

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerHand]:
        quads_cards = get_duplicate_cards(cards, num_duplicate=4)
        assert len(quads_cards) <= 1, quads_cards
        quads = len(quads_cards) == 1

        if quads:
            result = []
            for card in cards:
                if card == quads_cards[0]:
                    result.append(card)
            result.append(get_remainder_of_pairs(cards, quads_cards)[-1])
        else:
            result = ace_sort(cards)[-5:]
        assert len(result) == 5, result
        result = cast(PokerHand, result)
        return quads, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            quads1 = get_duplicate_cards(list(self.final_hand), num_duplicate=4)
            quads2 = get_duplicate_cards(list(other.final_hand), num_duplicate=4)
            if quads1 == quads2:
                remain1 = get_remainder_of_pairs(self.final_hand, quads1)
                remain2 = get_remainder_of_pairs(other.final_hand, quads1)
                return lt_cards(remain1, remain2)
            else:
                return lt_cards(quads1, quads2)
        else:
            return self.name > other.name


class FullHouse(HandType):
    name: HandRanking = HandRanking.FULLHOUSE

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerHand]:
        trips = get_duplicate_cards(cards, num_duplicate=3)
        assert len(trips) <= 2, trips
        if len(trips) == 2:
            pair = trips[:1]
            trips = trips[-1:]
        elif len(trips) == 1:
            pair = get_duplicate_cards(cards, num_duplicate=2)[-1:]
        else:
            pair = []

        fullhouse = len(trips) > 0 and len(pair) > 0
        if fullhouse:
            result = []
            for card in cards:
                if card in trips:
                    result.append(card)
            for card in cards:
                if card in pair:
                    result.append(card)
            result = result[:5]
        else:
            result = ace_sort(cards)[-5:]
        assert len(result) == 5, result
        result = cast(PokerHand, result)
        return fullhouse, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            trips1 = get_duplicate_cards(list(self.final_hand), num_duplicate=3)
            trips2 = get_duplicate_cards(list(other.final_hand), num_duplicate=3)

            pair1 = get_duplicate_cards(list(self.final_hand), num_duplicate=2)
            pair2 = get_duplicate_cards(list(other.final_hand), num_duplicate=2)
            if trips1 == trips2:
                return lt_cards(pair1, pair2)
            else:
                return lt_cards(trips1, trips2)
        else:
            return self.name > other.name


class Flush(HandType):
    name: HandRanking = HandRanking.FLUSH

    @classmethod
    def _all_flush_cards(cls, cards: List[PokerCard]) -> List[PokerCard]:
        suit_counts = {suit: 0 for suit in PokerSuit}
        for suit in PokerSuit:
            for card in cards:
                if card.has_suit(suit):
                    suit_counts[suit] += 1
        flush_suit = None
        for suit in PokerSuit:
            if suit_counts[suit] >= 5:
                flush_suit = suit
        flush_cards = []
        if flush_suit is not None:
            for card in cards:
                if card.has_suit(flush_suit):
                    flush_cards.append(card)
        return ace_sort(flush_cards)

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerHand]:
        flush_cards = cls._all_flush_cards(cards)
        flush = len(flush_cards) >= 5
        if flush:
            result = flush_cards[-5:]
        else:
            result = ace_sort(cards)[-5:]
        assert len(result) == 5, result
        result = cast(PokerHand, result)
        return flush, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            return lt_cards(list(self.final_hand), list(other.final_hand))
        else:
            return self.name > other.name


class Straight(HandType):
    name: HandRanking = HandRanking.STRAIGHT

    @classmethod
    def _all_straight_cards(cls, cards: List[PokerCard]) -> List[PokerCard]:
        sorted_cards = sorted(cards)
        ace = PokerCard("a", "s")
        king = PokerCard("k", "s")
        straight_cards = []
        for prev, curr in zip(sorted_cards[:-1], sorted_cards[1:]):
            if curr - prev == 1:
                if prev not in straight_cards:
                    straight_cards.append(prev)
                straight_cards.append(curr)
            elif len(straight_cards) >= 5:
                break
            else:
                straight_cards = []

        # Handle Broadway Straight
        if king in straight_cards and ace in sorted_cards:
            ace_card = None
            for card in sorted_cards:
                if card == ace:
                    ace_card = card
            assert ace_card is not None
            straight_cards.append(ace_card)

        return ace_sort(straight_cards, straight=True)

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerHand]:
        straight_cards = cls._all_straight_cards(cards)
        straight = len(straight_cards) >= 5
        if straight:
            result = straight_cards[-5:]
        else:
            result = ace_sort(cards)[-5:]
        assert len(result) == 5, result
        result = cast(PokerHand, result)
        return straight, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            return lt_cards(self.final_hand, other.final_hand)
        else:
            return self.name > other.name


class Trips(HandType):
    name: HandRanking = HandRanking.TRIPS

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerHand]:
        trips_cards = get_duplicate_cards(cards, num_duplicate=3)
        trips = len(trips_cards) > 0
        if trips:
            remaining = get_remainder_of_pairs(cards, trips_cards[-1:])
            result = []
            for card in cards:
                if card == trips_cards[-1]:
                    result.append(card)
            result = result + remaining[-2:]
        else:
            result = ace_sort(cards)[-5:]
        assert len(result) == 5, result
        result = cast(PokerHand, result)
        return trips, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            trips1 = get_duplicate_cards(list(self.final_hand), num_duplicate=3)[:-1]
            trips2 = get_duplicate_cards(list(other.final_hand), num_duplicate=3)[:-1]
            if trips1 == trips2:
                remain1 = get_remainder_of_pairs(self.final_hand, trips1)
                remain2 = get_remainder_of_pairs(other.final_hand, trips2)
                return lt_cards(remain1, remain2)
            else:
                return lt_cards(trips1, trips2)
        else:
            return self.name > other.name


class TwoPair(HandType):
    name: HandRanking = HandRanking.TWOPAIR

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerHand]:
        pair_cards = get_duplicate_cards(cards, num_duplicate=2)
        twopair = len(pair_cards) >= 2
        if twopair:
            pair_cards = pair_cards[-2:]
            result = []
            for card in ace_sort(cards):
                if card in pair_cards:
                    result.append(card)
            remaining = get_remainder_of_pairs(cards, pair_cards)
            result.append(remaining[-1])
        else:
            result = ace_sort(cards)[-5:]
        assert len(result) == 5, result
        result = cast(PokerHand, result)
        return twopair, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            pairs1 = get_duplicate_cards(list(self.final_hand), num_duplicate=2)[-2:]
            pairs2 = get_duplicate_cards(list(other.final_hand), num_duplicate=2)[-2:]
            if pairs1 == pairs2:
                remain1 = get_remainder_of_pairs(self.final_hand, pairs1)
                remain2 = get_remainder_of_pairs(other.final_hand, pairs2)
                return lt_cards(remain1, remain2)
            else:
                return lt_cards(pairs1, pairs2)

        else:
            return self.name > other.name


class Pair(HandType):
    name: HandRanking = HandRanking.PAIR

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerHand]:
        pair_cards = get_duplicate_cards(cards, num_duplicate=2)
        pair = len(pair_cards) >= 1
        if pair:
            pair_cards = pair_cards[-1:]
            remaining = []
            result = []
            for card in ace_sort(cards):
                if card in pair_cards:
                    result.append(card)
            remaining = get_remainder_of_pairs(cards, pair_cards)
            result.extend(remaining[-3:])
        else:
            result = ace_sort(cards)[-5:]
        assert len(result) == 5, result
        result = cast(PokerHand, result)
        return pair, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            pairs1 = get_duplicate_cards(list(self.final_hand), num_duplicate=2)[-1:]
            pairs2 = get_duplicate_cards(list(other.final_hand), num_duplicate=2)[-1:]
            if pairs1 == pairs2:
                remain1 = get_remainder_of_pairs(self.final_hand, pairs1)
                remain2 = get_remainder_of_pairs(other.final_hand, pairs2)
                return lt_cards(remain1, remain2)
            else:
                return lt_cards(pairs1, pairs2)

        else:
            return self.name > other.name


class High(HandType):
    name: HandRanking = HandRanking.HIGH

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerHand]:
        result = ace_sort(cards)[-5:]
        return True, cast(PokerHand, result)

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            return lt_cards(self.final_hand, other.final_hand)
        else:
            return self.name > other.name


HANDRANKING_DICT = OrderedDict(
    {
        HandRanking.ROYAL: Royal,
        HandRanking.STRAIGHTFLUSH: StraightFlush,
        HandRanking.QUADS: Quads,
        HandRanking.FULLHOUSE: FullHouse,
        HandRanking.FLUSH: Flush,
        HandRanking.STRAIGHT: Straight,
        HandRanking.TRIPS: Trips,
        HandRanking.TWOPAIR: TwoPair,
        HandRanking.PAIR: Pair,
        HandRanking.HIGH: High,
    }
)


def get_final_hand_made(
    board: PokerHand, hand: PokerHole
) -> Tuple[HandRanking, PokerHand]:
    all_cards = list(board) + list(hand)
    hand_type, result = None, None
    for hand_type in HANDRANKING_DICT:
        is_hand_type, result = HANDRANKING_DICT[hand_type].check(all_cards)
        if is_hand_type:
            break
    assert hand_type is not None and result is not None
    return hand_type, result


def rank_hands(board: PokerBoard, hands: List[PokerHole]) -> List[int]:
    assert len(board) == 5
    for card in board:
        assert card is not None
    final_board = cast(PokerHand, list(board))

    hand_types: List[HandRanking] = []
    final_hands: List[HandType] = []

    for hand in hands:
        hand_type, final_hand = get_final_hand_made(final_board, hand)
        hand_types.append(hand_type)
        final_hands.append(HANDRANKING_DICT[hand_type](final_hand))

    indices = list(range(len(hands)))
    sorted_results = sorted(zip(indices, final_hands), reverse=True, key=lambda x: x[1])
    ranks = [-1] * len(hands)
    rank = 0
    tie_count = 1
    for index in range(len(sorted_results) - 1):
        i, hand = sorted_results[index]
        ranks[i] = rank
        next_i, next_hand = sorted_results[index + 1]
        if hand != next_hand:
            rank += tie_count
            tie_count = 1
        else:
            tie_count += 1
        if index == len(sorted_results) - 2:
            # Make sure to add rank for last hand
            ranks[next_i] = rank
    return ranks
