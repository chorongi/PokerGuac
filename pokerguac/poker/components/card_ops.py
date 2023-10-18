from typing import List, Sequence
from .card import PokerCard


def ace_sort(cards: Sequence[PokerCard], straight: bool = False) -> List[PokerCard]:
    ace = PokerCard("a", "s")
    king = PokerCard("k", "s")
    if ace not in cards or (straight and king not in cards):
        return sorted(cards)
    else:
        ace_cards = []
        remaining = []
        for card in cards:
            if card == ace:
                ace_cards.append(card)
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
    """
    If you have AAATT23 in cards, function will return [A, T]
    """
    card_count = get_cnt_dict(cards)
    pair_cards = []
    for card in card_count:
        if card_count[card] == num_duplicate:
            pair_cards.append(card)
    pair_cards = ace_sort(pair_cards)
    return pair_cards


def get_remainder_of_pairs(
    cards: Sequence[PokerCard], pair_cards: List[PokerCard]
) -> List[PokerCard]:
    """
    Args
    ----
    cards (List[PokerCard]): List of all cards to consider as hand
    pair_cards (List[PokerCard]): List of all cards that was matched with at least a pair (includes trips, quads)
    Returns
    -------
    ace sorted remainder that was not matched with at least a pair (includes trips, quads)
    """
    remainder = []
    for card in cards:
        if card not in pair_cards:
            remainder.append(card)
    return ace_sort(remainder)


def lt_cards(cards1: Sequence[PokerCard], cards2: Sequence[PokerCard]) -> bool:
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

    # All cards are equal
    return False
