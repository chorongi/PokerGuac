import arcade
from .constants import DEFAULT_FONT_SIZE, DEFAULT_FONT
from .card import ArcadePokerCard
from ..poker import PokerPlayer
from typing import Tuple, List


class ArcadePokerPlayer:
    default_font_size: float = DEFAULT_FONT_SIZE
    default_font: str = DEFAULT_FONT
    player_card_list: arcade.SpriteList
    player_mat_list: arcade.SpriteList
    arcade_cards: List[ArcadePokerCard]
    player: PokerPlayer

    def __init__(self, poker_player: PokerPlayer, num_cards: int):
        self.player = poker_player
        self.arcade_cards = []
        self.num_cards = num_cards

    def draw_mat(
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

    def draw_cards(
        self, cards: List[ArcadePokerCard], card_positions: List[Tuple[float, float]]
    ):
        # Draw player cards
        assert len(cards) == len(card_positions) == self.num_cards
        self.player_card_list = arcade.SpriteList()
        for card_pos, card in zip(card_positions, cards):
            card.position = card_pos
            self.player_card_list.append(card)
        self.player_card_list.draw()

    def draw(
        self,
        player_pos: Tuple[float, float],
        bet_pos: Tuple[float, float],
        card_positions: List[Tuple[float, float]],
        card_width: float,
    ):
        assert len(card_positions) > 0
        card_h, card_w = ArcadePokerCard.get_size(card_width)
        player_x, player_y = player_pos
        card_x, card_y = card_positions[0]
        margin = card_w / 3
        betx, bety = bet_pos
        self.arcade_cards = []

        # Draw player mat
        self.draw_mat((card_h, card_w), card_positions)

        # Draw player cards
        if self.player.hole is not None:
            for card in self.player.hole:
                self.arcade_cards.append(ArcadePokerCard(card, card_w))
            self.draw_cards(self.arcade_cards, card_positions)

        # Draw player name
        arcade.draw_text(
            self.player,
            card_x - card_w / 2,
            card_y - card_h / 2 - margin,
            arcade.color.BLACK,
            self.default_font_size,
            font_name=self.default_font,
        )

        # Draw player status
        status = self.player.status
        arcade.draw_text(
            status,
            betx,
            bety,
            arcade.color.BLACK,
            self.default_font_size,
            font_name=self.default_font,
        )

        # Draw player action (bet)
        bet = self.player.stage_bet
        arcade.draw_text(
            f"$ {bet:.02f}",
            betx,
            bety + margin,
            arcade.color.BLACK,
            self.default_font_size,
            font_name=self.default_font,
        )

    @classmethod
    def draw_empty_player(cls, player_position: Tuple[float, float]):
        arcade.draw_text(
            "Empty",
            player_position[0],
            player_position[1],
            arcade.color.BLACK,
            DEFAULT_FONT_SIZE,
            font_name=DEFAULT_FONT,
        )
