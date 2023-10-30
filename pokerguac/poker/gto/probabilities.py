import itertools
import numpy as np
from typing import Set, List, Tuple, cast

from ..components.card import PokerHole, PokerBoard, PokerCard
from ..components.rules import rank_hands
from ..components.constants import POKER_CARD_DECK, NUMBER_STRING_TO_INT

NUM_BOARD_CARDS = 5


def get_remaining_cards(used_cards: List[PokerCard]) -> List[PokerCard]:
    remaining_cards = []
    for card_str in POKER_CARD_DECK:
        card1 = PokerCard.from_symbol(card_str)
        is_remain = True
        for card2 in used_cards:
            if card1.equal(card2):
                is_remain = False
                break
        if is_remain:
            remaining_cards.append(card1)
    return remaining_cards


def get_all_possible_villain_holes(used_cards: List[PokerCard]) -> List[PokerHole]:
    remain_cards = get_remaining_cards(used_cards)
    villain_cards = list(itertools.combinations(remain_cards, 2))
    return villain_cards


def get_all_possible_boards(
    used_cards: List[PokerCard], board: PokerBoard
) -> List[PokerBoard]:
    assert len(board) == NUM_BOARD_CARDS
    remain_cards = get_remaining_cards(used_cards)
    num_left_board_cards = board.count(None)
    assert num_left_board_cards >= 0 and num_left_board_cards <= NUM_BOARD_CARDS
    all_boards = list(itertools.combinations(remain_cards, num_left_board_cards))
    board_cards: List[PokerCard] = list(filter(lambda card: card is not None, board))  # type: ignore
    all_boards = [
        cast(PokerBoard, board_cards + list(remain_board))
        for remain_board in all_boards
    ]
    return all_boards


def compute_hand_strength(
    hole: PokerHole, board: PokerBoard
) -> Tuple[float, float, float]:
    card_board: List[PokerCard] = list(filter(lambda card: card is not None, board))  # type: ignore
    used_cards = set(hole)
    used_cards.update(set(card_board))
    all_boards = get_all_possible_boards(used_cards, board)
    avg_winning_prob = 0.0
    avg_draw_prob = 0.0
    avg_losing_prob = 0.0
    num_cases = 0
    for simul_board in all_boards:
        simul_used_cards = set()
        simul_used_cards.update(hole)
        simul_used_cards.update(set(simul_board))
        villain_holes = get_all_possible_villain_holes(simul_used_cards)
        num_cases += len(villain_holes)
        villain_holes.insert(0, hole)
        ranks, _ = rank_hands(simul_board, villain_holes)
        my_rank = ranks[0]
        villain_ranks = np.array(ranks[1:])
        avg_losing_prob += np.sum(my_rank > villain_ranks)
        avg_winning_prob += np.sum(my_rank < villain_ranks)
        avg_draw_prob += np.sum(my_rank == villain_ranks)
    avg_winning_prob = float(avg_winning_prob / num_cases)
    avg_draw_prob = float(avg_draw_prob / num_cases)
    avg_losing_prob = float(avg_losing_prob / num_cases)
    assert avg_winning_prob + avg_draw_prob + avg_losing_prob == 1
    return avg_winning_prob, avg_draw_prob, avg_losing_prob
