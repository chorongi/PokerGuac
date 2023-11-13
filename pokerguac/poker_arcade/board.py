import arcade
import arcade.color
import arcade.csscolor
from .constants import DEFAULT_FONT_SIZE, DEFAULT_FONT, POT_FONT_SIZE, BUTTON_FONT_SIZE
from .card import ArcadePokerCard
from ..poker import PokerTable
from typing import Tuple, List


class ArcadePokerBoard:
    default_font_size: float = DEFAULT_FONT_SIZE
    default_font: str = DEFAULT_FONT
    button_font_size: float = BUTTON_FONT_SIZE
    pot_font_size: float = POT_FONT_SIZE
    player_card_list: arcade.SpriteList
    player_mat_list: arcade.SpriteList
    arcade_cards: List[ArcadePokerCard]
    table: PokerTable

    def __init__(self, poker_table: PokerTable, num_board_cards: int):
        self.table = poker_table
        self.arcade_cards = []
        self.num_cards = num_board_cards

    def _draw_mat(
        self, card_size: Tuple[int, int], card_positions: List[Tuple[float, float]]
    ):
        # Draw player mats
        assert len(card_positions) == self.num_cards
        self.player_mat_list = arcade.SpriteList()
        card_h, card_w = card_size
        for card_pos in card_positions:
            mat = arcade.SpriteSolidColor(
                card_w,
                card_h,
                arcade.csscolor.DARK_OLIVE_GREEN,
            )
            mat.position = card_pos
            self.player_mat_list.append(mat)
        self.player_mat_list.draw()

    def _draw_cards(
        self, cards: List[ArcadePokerCard], card_positions: List[Tuple[float, float]]
    ):
        # Draw player cards
        assert len(cards) == len(card_positions)
        assert len(cards) <= self.num_cards
        self.player_card_list = arcade.SpriteList()
        for card_pos, card in zip(card_positions, cards):
            card.position = card_pos
            self.player_card_list.append(card)
        self.player_card_list.draw()

    def draw_button(
        self, button_pos: Tuple[float, float], radius: float = BUTTON_FONT_SIZE
    ):
        bx, by = button_pos
        arcade.draw_circle_filled(bx, by, radius, arcade.color.VANILLA)
        arcade.draw_text(
            "B",
            bx - radius / 2,
            by - radius / 2,
            color=arcade.color.BLACK,
            font_size=radius,
            bold=True,
        )

    def draw_pot_size(self, pot_pos: Tuple[float, float]):
        potx, poty = pot_pos
        arcade.draw_text(
            f"Pot Size: ${self.table.get_pot_size():.02f} ({self.table.get_pot_size()/self.table.big_blind:.02f} BB)",
            potx,
            poty,
            color=arcade.color.BLACK,
            font_size=self.pot_font_size,
            bold=True,
            anchor_x="center",
        )

    def draw_board_cards(
        self, card_width: float, card_positions: List[Tuple[float, float]]
    ):
        card_h, card_w = ArcadePokerCard.get_size(card_width)
        self.arcade_cards = []

        # Draw player mat
        self._draw_mat((card_h, card_w), card_positions)

        # Draw player cards
        for card in self.table.board:
            if card is not None:
                self.arcade_cards.append(ArcadePokerCard(card, card_width))
        self._draw_cards(self.arcade_cards, card_positions[: len(self.arcade_cards)])
