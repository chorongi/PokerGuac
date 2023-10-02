import numpy as np

from typing import List

from . import POKER_CARD_DECK
from .player import PokerPlayer


def PokerTable():
    def __init__(self, players: List[PokerPlayer]):
        self.cards = POKER_CARD_DECK
        self.players = players
        self.button = np.random.choice(np.arange(len(self.players)), 1)

    def deal():

    def preflop():

    def flop():

    def turn():

    def river():

    def step()
