from poker import PokerTable, PokerPlayer, PokerHole, PokerBoard


def visualize_player(player: PokerPlayer):
    pass


def visualize_table(table: PokerTable):
    pass


def visualize_hole(hand: PokerHole):
    pass


import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "PokerGuac"


class PokerGuac(arcade.Window):
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.AMAZON)
