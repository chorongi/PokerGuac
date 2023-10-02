

class PokerPlayer:
    stack: float
    _hand: Tuple[]

    def __init__(self, buy_in: float):
        self.stack = buy_in
        self._hand = Tuple[PokerCard, PokerCard]

    @hand.setter
    def hand(self, hand):



    def get_effective_stack(self, big_blind: float) -> float:
        return self.stack / big_blind
