import arcade
import math
import numpy as np

from ..poker import poker_tournament_init
from ..poker import PokerPlayer, PokerTable, ALL_AGENT_TYPES
from ..poker.components.constants import MAX_NUM_PLAYERS, BOARD_NUM_CARDS
from .board import ArcadePokerBoard
from .card import ArcadePokerCard
from .player import ArcadePokerPlayer
from .constants import (
    POT_FONT_SIZE,
    DEFAULT_FONT,
    DEFAULT_FONT_SIZE,
    BOARD_CARD_RATIO,
    PLAYER_CARD_RATIO,
    BETTING_ZONE_RATIO_H,
    BETTING_ZONE_RATIO_W,
    PLAYER_ZONE_RATIO_H,
    PLAYER_ZONE_RATIO_W,
    MARGIN_RATIO,
)
from typing import List, Tuple, Optional


class PokerTableScreen(arcade.View):
    players: List[Optional[ArcadePokerPlayer]]
    board: ArcadePokerBoard
    table: PokerTable
    default_font_size: float = DEFAULT_FONT_SIZE
    default_font: str = DEFAULT_FONT
    total_time: float = 0.0

    def __init__(self, window: arcade.Window, table: PokerTable):
        super().__init__(window)
        arcade.set_background_color(arcade.color.AMAZON)  # type: ignore hkwark
        self.table = table
        self.player_card_size = ArcadePokerCard.get_size(
            self.window.width * PLAYER_CARD_RATIO
        )
        self.board_card_size = ArcadePokerCard.get_size(
            self.window.width * BOARD_CARD_RATIO
        )
        self.margin = round(self.window.width * MARGIN_RATIO)
        for player in self.table.players:
            if player is not None:
                player.join_next_hand()
        self.players = [
            ArcadePokerPlayer(player, self.table.num_player_cards)
            if player is not None
            else None
            for player in table.players
        ]
        self.board = ArcadePokerBoard(table, BOARD_NUM_CARDS)
        self.total_time = 0

    def index_to_player_position(self, index: int) -> Tuple[float, float]:
        major_axis = self.window.width * PLAYER_ZONE_RATIO_W
        minor_axis = self.window.height * PLAYER_ZONE_RATIO_H
        cx = self.window.width / 2 - self.margin
        cy = self.window.height / 2 + self.player_card_size[0] / 2

        index = MAX_NUM_PLAYERS - index - 1
        player_pos = (
            cx + major_axis / 2 * math.cos(2 * math.pi / MAX_NUM_PLAYERS * index),
            cy + minor_axis / 2 * math.sin(2 * math.pi / MAX_NUM_PLAYERS * index),
        )
        return player_pos

    def index_to_player_betting_position(self, index: int) -> Tuple[float, float]:
        major_axis = self.window.width * BETTING_ZONE_RATIO_W
        minor_axis = self.window.height * BETTING_ZONE_RATIO_H
        cx = self.window.width / 2 - self.margin
        cy = self.window.height / 2

        index = MAX_NUM_PLAYERS - index - 1
        betting_pos = (
            cx + major_axis / 2 * math.cos(2 * math.pi / MAX_NUM_PLAYERS * index),
            cy + minor_axis / 2 * math.sin(2 * math.pi / MAX_NUM_PLAYERS * index),
        )
        return betting_pos

    def index_to_board_card_position(self, index: int) -> Tuple[float, float]:
        board_card_pos = (
            self.window.width / 2
            - BOARD_NUM_CARDS // 2 * self.board_card_size[1]
            + index * self.board_card_size[1]
            + (index - BOARD_NUM_CARDS // 2) * self.margin,
            self.window.height / 2,
        )
        return board_card_pos

    def button_position(self) -> Tuple[float, float]:
        assert self.table.button is not None
        major_axis = self.window.width * BETTING_ZONE_RATIO_W
        minor_axis = self.window.height * BETTING_ZONE_RATIO_H
        cx = self.window.width / 2 - self.margin
        cy = self.window.height / 2
        index = self.table.button
        index = MAX_NUM_PLAYERS - index - 1
        button_pos = (
            cx
            + major_axis / 2 * math.cos(2 * math.pi / MAX_NUM_PLAYERS * index)
            + self.margin / 2,
            cy
            + minor_axis / 2 * math.sin(2 * math.pi / MAX_NUM_PLAYERS * index)
            - self.margin,
        )
        return button_pos

    def pot_display_position(self) -> Tuple[float, float]:
        pot_x = self.window.width / 2
        pot_y = self.window.height / 2 + self.board_card_size[0] / 2 + POT_FONT_SIZE
        return (pot_x, pot_y)

    def setup(self):
        """Set up the game variables. Call to re-start the game."""
        # Create your sprites and sprite lists here
        pass

    def draw_players(self):
        for i, player in enumerate(self.players):
            player_pos = self.index_to_player_position(i)
            if player is not None:
                bet_pos = self.index_to_player_betting_position(i)
                card_positions = [
                    (
                        player_pos[0]
                        + j * (self.player_card_size[1] + self.margin / 2),
                        player_pos[1] - self.margin,
                    )
                    for j in range(self.table.num_player_cards)
                ]
                player.draw(
                    player_pos, bet_pos, card_positions, self.player_card_size[1]
                )
            else:
                ArcadePokerPlayer.draw_empty_player(player_pos)

    def draw_board(self):
        board_card_pos = [
            self.index_to_board_card_position(i) for i in range(BOARD_NUM_CARDS)
        ]
        self.board.draw_board_cards(self.board_card_size[1], board_card_pos)
        self.board.draw_pot_size(self.pot_display_position())
        if self.table.active:
            button_pos = self.button_position()
            self.board.draw_button(button_pos, self.margin / 2)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()
        # Call draw() on all your sprite lists below
        self.draw_players()
        self.draw_board()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        if self.table.can_activate():
            self.table.activate_table()
        # if self.table.finished():
        #     print("=====================================================")
        #     print(self.table.player_rankings_report()[1])

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        self.table.step()

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass
