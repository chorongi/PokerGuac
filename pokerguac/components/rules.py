from .card import PokerCard, PokerBoard, PokerHand
from . import PokerSuit
from enum import Enum
from typing import Tuple, OrderedDict, List, cast
from abc import ABC, abstractmethod


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


def ace_sort(cards: List[PokerCard], straight: bool = False) -> List[PokerCard]:
    ace = PokerCard("a", "s")
    king = PokerCard("k", "s")
    if ace not in cards or (straight and king not in cards):
        return sorted(cards)
    else:
        ace_cards = []
        remaining = []
        for card in cards:
            if card == ace:
                ace_cards.append(ace)
            else:
                remaining.append(card)
        assert len(ace_cards)

        return sorted(remaining) + ace_cards


def get_cnt_dict(cards: List[PokerCard]):
    card_count = {}
    for card in cards:
        count = card_count.get(card, 0)
        card_count[card] = count + 1
    return card_count


def get_duplicate_cards(cards: List[PokerCard], num_duplicate: int = 2):
    card_count = get_cnt_dict(cards)
    pair_cards = []
    for card in card_count:
        if card_count[card] == num_duplicate:
            pair_cards.append(card)
    pair_cards = ace_sort(pair_cards)
    pair_cards.reverse()
    return pair_cards


def lt_cards(cards1: List[PokerCard], cards2: List[PokerCard]):
    assert len(cards1) == len(cards2)
    remaining1 = ace_sort(cards1)
    remaining2 = ace_sort(cards2)
    remaining1.reverse()
    remaining2.reverse()
    ace = PokerCard("a", "s")
    for card1, card2 in zip(cards1, cards2):
        if ace == card1 and ace != card2:
            return False
        elif ace != card1 and ace == card2:
            return True
        elif card1 == card2:
            continue
        else:
            return card1 < card2


def lt_remainder(
    board1: PokerBoard,
    board2: PokerBoard,
    pairs1: List[PokerCard],
    pairs2: List[PokerCard],
):
    remaining1 = []
    remaining2 = []
    for card in board1:
        if card not in pairs1:
            remaining1.append(card)
    for card in board2:
        if card not in pairs2:
            remaining2.append(card)
    return lt_cards(remaining1, remaining2)


class HandType(ABC):
    final_board: PokerBoard
    name: HandRanking

    def __init__(self, board: PokerBoard):
        success, self.final_board = self.check(list(board))
        assert success

    @classmethod
    @abstractmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerBoard]:
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
        return self.__class__ == other.__class__ and sorted(self.final_board) == sorted(
            other.final_board
        )


class Royal(HandType):
    name: HandRanking = HandRanking.ROYAL

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerBoard]:
        straightflush, result = StraightFlush.check(cards)
        broadway = cls.is_broadway(cards)
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
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerBoard]:
        sorted_cards = sorted(cards)
        straightflush_count = 0
        straightflush_cards = []
        ace = PokerCard("a", "s")
        king = PokerCard("k", "s")
        for prev, curr in zip(sorted_cards[:-1], sorted_cards[1:]):
            if curr - prev == 1 and prev.suit_eq(curr):
                straightflush_count += 1
                if prev not in straightflush_cards:
                    straightflush_cards.append(prev)
                else:
                    straightflush_cards.append(curr)
            else:
                straightflush_count = 0
                straightflush_cards = []

        if king in straightflush_cards and ace in sorted_cards:
            ace_card = None
            king_card = None
            for card in sorted_cards:
                if card == ace:
                    ace_card = card
            for card in straightflush_cards:
                if card == king:
                    king_card = card
            assert ace_card is not None and king_card is not None
            if ace_card.suit_eq(king_card):
                straightflush_count += 1
                straightflush_cards.append(ace_card)

        straightflush = len(straightflush_cards) >= 5
        if straightflush:
            result = cast(PokerBoard, ace_sort(straightflush_cards, straight=True)[-5:])
        else:
            result = cast(PokerBoard, ace_sort(cards)[-5:])
        assert len(result) == 5, result
        return straightflush, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            highest_cards = [
                ace_sort(list(self.final_board), straight=True)[-1],
                ace_sort(list(other.final_board), straight=True)[-1],
            ]
            return highest_cards == ace_sort(highest_cards)
        else:
            return self.name > other.name


class Quads(HandType):
    name: HandRanking = HandRanking.QUADS

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerBoard]:
        sorted_cards = ace_sort(cards)
        card_count = get_cnt_dict(sorted_cards)
        quads = False
        result = cast(PokerBoard, sorted_cards[-5:])
        for hash_card in card_count:
            if card_count[hash_card] == 4:
                quads = True
                result = []
                remaining = []
                for card in sorted_cards:
                    if hash_card == card:
                        result.append(card)
                    else:
                        remaining.append(card)
                result.append(ace_sort(remaining)[-1])
                result = cast(PokerBoard, result)
        assert len(result) == 5, result
        return quads, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            quads1 = get_duplicate_cards(list(self.final_board), num_duplicate=4)
            quads2 = get_duplicate_cards(list(other.final_board), num_duplicate=4)
            assert quads1 == quads2
            return lt_remainder(self.final_board, other.final_board, quads1, quads2)
        else:
            return self.name > other.name


class FullHouse(HandType):
    name: HandRanking = HandRanking.FULLHOUSE

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerBoard]:
        sorted_cards = ace_sort(cards)
        card_count = get_cnt_dict(sorted_cards)
        trips = []
        pair = []
        trip_card = None
        pair_card = None
        for hash_card in card_count:
            if card_count[hash_card] == 3:
                if trip_card is not None and trip_card > hash_card:
                    continue
                else:
                    for card in sorted_cards:
                        if card == hash_card:
                            trips.append(card)
            if card_count[hash_card] == 2:
                if pair_card is not None and pair_card > hash_card:
                    continue
                else:
                    for card in sorted_cards:
                        if card == hash_card:
                            pair.append(card)
        fullhouse = len(trips) == 3 and len(pair) == 2
        if fullhouse:
            result = cast(PokerBoard, trips + pair)
        else:
            result = cast(PokerBoard, sorted_cards[-5:])
        assert len(result) == 5, result
        return fullhouse, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            trips1 = get_duplicate_cards(list(self.final_board), num_duplicate=3)
            trips2 = get_duplicate_cards(list(other.final_board), num_duplicate=3)

            pair1 = get_duplicate_cards(list(self.final_board), num_duplicate=2)
            pair2 = get_duplicate_cards(list(other.final_board), num_duplicate=2)
            if trips1 == trips2:
                return lt_cards(pair1, pair2)
            else:
                return lt_cards(trips1, trips2)
        else:
            return self.name > other.name


class Flush(HandType):
    name: HandRanking = HandRanking.FLUSH

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerBoard]:
        sorted_cards = ace_sort(cards)
        suit_counts = {suit: 0 for suit in PokerSuit}
        for suit in PokerSuit:
            for card in sorted_cards:
                if card.has_suit(suit):
                    suit_counts[suit] += 1
        flush = False
        result = cast(PokerBoard, sorted_cards[-5:])
        for suit in PokerSuit:
            if suit_counts[suit] >= 5:
                flush = True
                flush_cards = []
                for card in sorted_cards:
                    if card.has_suit(suit):
                        flush_cards.append(card)
                result = cast(PokerBoard, ace_sort(flush_cards)[-5:])
        assert len(result) == 5, result
        return flush, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            return lt_cards(list(self.final_board), list(other.final_board))
        else:
            return self.name > other.name


class Straight(HandType):
    name: HandRanking = HandRanking.STRAIGHT

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerBoard]:
        sorted_cards = ace_sort(cards)
        ace = PokerCard("a", "s")
        king = PokerCard("k", "s")

        straight_count = 0
        straight_cards = []
        for prev, curr in zip(sorted_cards[:-1], sorted_cards[1:]):
            if curr - prev == 1:
                straight_count += 1
                if prev not in straight_cards:
                    straight_cards.append(prev)
                else:
                    straight_cards.append(curr)
            else:
                straight_count = 0
                straight_cards = []

        if king in straight_cards and ace in sorted_cards:
            for card in sorted_cards:
                if card == ace:
                    straight_count += 1
                    straight_cards.append(card)

        straight = straight_count >= 5
        if straight:
            result = cast(PokerBoard, ace_sort(straight_cards[-5:], straight=True))
        else:
            result = cast(PokerBoard, sorted_cards[-5:])
        assert len(result) == 5, result
        return straight, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            highest_cards = [
                ace_sort(list(self.final_board), straight=True)[-1],
                ace_sort(list(other.final_board), straight=True)[-1],
            ]
            return highest_cards == ace_sort(highest_cards)
        else:
            return self.name > other.name


class Trips(HandType):
    name: HandRanking = HandRanking.TRIPS

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerBoard]:
        sorted_cards = ace_sort(cards)
        card_count = get_cnt_dict(sorted_cards)
        trips_cards = []
        for hash_card in card_count:
            if card_count[hash_card] == 3:
                for card in sorted_cards:
                    if card == hash_card:
                        trips_cards.append(card)

        trips = len(trips_cards) >= 3
        if trips:
            trips_cards = ace_sort(trips_cards)[-3:]
            remaining = []
            for card in sorted_cards:
                if card not in trips_cards:
                    remaining.append(card)
            result = cast(PokerBoard, trips_cards + ace_sort(remaining)[-2:])
        else:
            result = cast(PokerBoard, sorted_cards[-5:])
        assert len(result) == 5, result
        return trips, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            trips1 = get_duplicate_cards(list(self.final_board), num_duplicate=3)
            trips2 = get_duplicate_cards(list(other.final_board), num_duplicate=3)
            if trips1 == trips2:
                return lt_remainder(self.final_board, other.final_board, trips1, trips2)
            else:
                return lt_cards(trips1, trips2)
        else:
            return self.name > other.name


class TwoPair(HandType):
    name: HandRanking = HandRanking.TWOPAIR

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerBoard]:
        sorted_cards = ace_sort(cards)
        card_count = get_cnt_dict(sorted_cards)
        twopair_cards = []
        for hash_card in card_count:
            if card_count[hash_card] == 2:
                for card in sorted_cards:
                    if card == hash_card:
                        twopair_cards.append(card)

        twopair = len(twopair_cards) >= 4
        if twopair:
            twopair_cards = ace_sort(twopair_cards)[-4:]
            remaining = []
            for card in sorted_cards:
                if card not in twopair_cards:
                    remaining.append(card)
            twopair_cards.append(ace_sort(remaining)[-1])
            result = cast(PokerBoard, twopair_cards)
        else:
            result = cast(PokerBoard, sorted_cards[-5:])
        assert len(result) == 5, result
        return twopair, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            pairs1 = get_duplicate_cards(list(self.final_board), num_duplicate=2)
            pairs2 = get_duplicate_cards(list(other.final_board), num_duplicate=2)
            if pairs1 == pairs2:
                return lt_remainder(self.final_board, other.final_board, pairs1, pairs2)
            else:
                return lt_cards(pairs1, pairs2)

        else:
            return self.name > other.name


class Pair(HandType):
    name: HandRanking = HandRanking.PAIR

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerBoard]:
        sorted_cards = ace_sort(cards)
        card_count = get_cnt_dict(sorted_cards)
        pair_cards = []
        for hash_card in card_count:
            if card_count[hash_card] == 2:
                for card in sorted_cards:
                    if card == hash_card:
                        pair_cards.append(card)

        pair = len(pair_cards) >= 2
        if pair:
            pair_cards = ace_sort(pair_cards)[-2:]
            remaining = []
            for card in sorted_cards:
                if card not in pair_cards:
                    remaining.append(card)
            pair_cards.extend(ace_sort(remaining)[-3:])
            result = cast(PokerBoard, pair_cards)
        else:
            result = cast(PokerBoard, sorted_cards[-5:])
        assert len(result) == 5, result
        return pair, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            pairs1 = get_duplicate_cards(list(self.final_board), num_duplicate=2)
            pairs2 = get_duplicate_cards(list(other.final_board), num_duplicate=2)
            if pairs1 == pairs2:
                return lt_remainder(self.final_board, other.final_board, pairs1, pairs2)
            else:
                return lt_cards(pairs1, pairs2)

        else:
            return self.name > other.name


class High(HandType):
    name: HandRanking = HandRanking.HIGH

    @classmethod
    def check(cls, cards: List[PokerCard]) -> Tuple[bool, PokerBoard]:
        sorted_cards = ace_sort(cards)
        result = cast(PokerBoard, sorted_cards[-5:])
        return True, result

    def __lt__(self, other):
        if self.__class__ == other.__class__:
            return lt_cards(list(self.final_board), list(other.final_board))
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
    board: PokerBoard, hand: PokerHand
) -> Tuple[HandRanking, PokerBoard]:
    all_cards = list(board) + list(hand)
    hand_type, result = None, None
    for hand_type in HANDRANKING_DICT:
        is_hand_type, result = HANDRANKING_DICT[hand_type].check(all_cards)
        if is_hand_type:
            break
    assert hand_type is not None and result is not None
    return hand_type, result


def rank_hands(board: PokerBoard, hands: List[PokerHand]) -> List[int]:
    hand_types: List[HandRanking] = []
    final_hands: List[HandType] = []
    for hand in hands:
        hand_type, board = get_final_hand_made(board, hand)
        hand_types.append(hand_type)
        final_hands.append(HANDRANKING_DICT[hand_type](board))

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
