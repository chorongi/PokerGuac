from .poker import PokerTable, PokerPlayer


def visualize_player(player: PokerPlayer):
    pass


def visualize_table(table: PokerTable):
    pass


import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "PokerGuac"


class PokerGuacEngine(arcade.Window):
    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.AMAZON)
