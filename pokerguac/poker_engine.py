import arcade
import math
import numpy as np

from .poker import PokerPlayer, PokerTable, AgentType, ALL_AGENT_TYPES
from .poker.components.constants import (
    MAX_NUM_PLAYERS,
    MIN_NUM_PLAYERS,
    BOARD_NUM_CARDS,
)
from .poker import build_action_agent
from .arcade import ArcadePokerCard
from typing import List, Optional, Tuple


SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
CARD_WIDTH_HEIGHT_RATIO = 1.452
SCREEN_TITLE = "PokerGuac"


def poker_tournament_init(
    player_names: List[str],
    agent_types: List[AgentType],
    num_players: int,
    small_blind: float = 1,
    big_blind: float = 3,
    max_num_buy_ins: int = 1,
    tournament_buy_in: float = 300,
    time_bank: Optional[float] = None,
):
    """
    Currently only supports one table
    """
    assert len(player_names) == len(agent_types)
    assert big_blind >= small_blind
    assert max_num_buy_ins >= 1
    assert tournament_buy_in >= big_blind
    assert len(player_names) <= num_players
    assert num_players >= MIN_NUM_PLAYERS
    players = [
        PokerPlayer(
            player_names[i],
            action_agent=build_action_agent(agent_types[i]),
            bank_roll=max_num_buy_ins * tournament_buy_in,
        )
        for i in range(num_players)
    ]
    table = PokerTable(
        num_players=num_players,
        big_blind=big_blind,
        small_blind=small_blind,
        min_buy_in=tournament_buy_in,
        max_buy_in=tournament_buy_in,
    )

    for player in players:
        player.join_tournament(tournament_buy_in, max_num_buy_ins, time_bank=time_bank)

    for player in players:
        table.seat_player(player)
    return table, players


def poker_cache_game_init(
    player_names: List[str],
    player_bank_rolls: List[float],
    agent_types: List[AgentType],
    num_players: int,
    small_blind: float = 1,
    big_blind: float = 3,
    min_buy_in: float = 100,
    max_buy_in: float = 300,
):
    """
    Currently only supports one table
    """
    assert len(player_names) == len(agent_types)
    assert big_blind >= small_blind
    assert max_buy_in >= min_buy_in
    assert len(player_names) <= num_players
    assert num_players >= MIN_NUM_PLAYERS
    players = [
        PokerPlayer(
            player_names[i],
            action_agent=build_action_agent(agent_types[i]),
            bank_roll=player_bank_rolls[i],
        )
        for i in range(num_players)
    ]
    table = PokerTable(
        num_players=num_players,
        big_blind=big_blind,
        small_blind=small_blind,
        min_buy_in=min_buy_in,
        max_buy_in=max_buy_in,
    )
    table.simulation_on()

    for player in players:
        player.try_buy_in(min_buy_in, max_buy_in)

    for player in players:
        table.seat_player(player)
    return table, players


class PokerGuacEngine(arcade.Window):
    players: List[PokerPlayer]
    table: PokerTable
    num_players: int
    index_to_player_inner_xy: List[Tuple[float, float]]
    index_to_player_outer_xy: List[Tuple[float, float]]
    index_to_board_card_cxcy: List[Tuple[float, float]]
    default_font_size: int = 9
    default_font: str = "Arial"

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)  # type: ignore hkwark
        arcade.set_background_color(arcade.color.AMAZON)  # type: ignore hkwark

        self.player_card_width = int(self.width / 30)
        self.board_card_width = int(self.width / 15)
        self.player_card_height = int(self.player_card_width * CARD_WIDTH_HEIGHT_RATIO)
        self.board_card_height = int(self.board_card_width * CARD_WIDTH_HEIGHT_RATIO)
        self.margin = int(self.width / 50)
        self.angle_margin = math.pi / 50
        self.index_to_board_card_cxcy = [
            (
                self.width / 2
                - BOARD_NUM_CARDS // 2 * self.board_card_width
                + i * self.board_card_width
                + (i - BOARD_NUM_CARDS // 2) * self.margin,
                self.height / 2,
            )
            for i in range(5)
        ]

        # Outer Circle
        major_axis = self.width * 0.85
        minor_axis = self.height * 0.85
        cx = self.width / 2 - self.margin
        cy = self.height / 2 + self.player_card_height / 2
        self.index_to_player_outer_xy = [
            (
                cx + major_axis / 2 * math.cos(2 * math.pi / MAX_NUM_PLAYERS * i),
                cy + minor_axis / 2 * math.sin(2 * math.pi / MAX_NUM_PLAYERS * i),
            )
            for i in range(MAX_NUM_PLAYERS)
        ]

        # Inner Circle (Where Betting / Button happens)
        major_axis = self.width * 0.65
        minor_axis = self.height * 0.65
        cx = self.width / 2 - self.margin
        cy = self.height / 2
        self.index_to_player_inner_xy = [
            (
                cx
                + major_axis
                / 2
                * math.cos(2 * math.pi / MAX_NUM_PLAYERS * i + self.angle_margin),
                cy
                + minor_axis
                / 2
                * math.sin(2 * math.pi / MAX_NUM_PLAYERS * i + self.angle_margin),
            )
            for i in range(MAX_NUM_PLAYERS)
        ]
        self.index_to_button_xy = [
            (
                cx
                + major_axis
                / 2
                * math.cos(2 * math.pi / MAX_NUM_PLAYERS * i - self.angle_margin),
                cy
                + minor_axis
                / 2
                * math.sin(2 * math.pi / MAX_NUM_PLAYERS * i - self.angle_margin),
            )
            for i in range(MAX_NUM_PLAYERS)
        ]

    def setup(self):
        """Set up the game variables. Call to re-start the game."""
        # Create your sprites and sprite lists here
        self.num_players = 9
        player_names = [
            "Alex",
            "Jenny",
            "Shane",
            "Jun",
            "Steve",
            "Jason",
            "Chris",
            "Sung",
            "Andrew",
        ]
        action_agent_types = list(
            np.random.choice(ALL_AGENT_TYPES, self.num_players, replace=True)
        )
        self.table, _ = poker_tournament_init(
            player_names, action_agent_types, self.num_players
        )

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()
        # Call draw() on all your sprite lists below
        self.draw_table()

    def draw_table(self):
        self.board_card_list = arcade.SpriteList()
        self.board_mat_list = arcade.SpriteList()

        self.draw_player()
        self.draw_board()

    def draw_player(self):
        self.player_mat_list = arcade.SpriteList()
        self.player_card_list = arcade.SpriteList()
        player_bets = self.table.get_per_player_bets()

        for i in range(self.num_players):
            player = self.table.players[i]
            player_x, player_y = self.index_to_player_outer_xy[i]
            card_pos1 = (
                player_x - self.player_card_width / 2 - self.margin / 10,
                player_y,
            )
            card_pos2 = (
                player_x + self.player_card_width / 2 + self.margin / 10,
                player_y,
            )
            betx, bety = self.index_to_player_inner_xy[i]
            if player is not None:
                # Draw player name
                arcade.draw_text(
                    player,
                    card_pos1[0] - self.player_card_width / 2,
                    card_pos1[1] - self.player_card_height / 2 - self.margin / 2,
                    arcade.color.BLACK,
                    self.default_font_size,
                    font_name=self.default_font,
                )
                # Draw player mats
                mat1 = arcade.SpriteSolidColor(
                    self.player_card_width,
                    self.player_card_height,
                    arcade.csscolor.DARK_OLIVE_GREEN,
                )
                mat1.position = card_pos1
                mat2 = arcade.SpriteSolidColor(
                    self.player_card_width,
                    self.player_card_height,
                    arcade.csscolor.DARK_OLIVE_GREEN,
                )
                mat2.position = card_pos2
                self.player_mat_list.append(mat1)
                self.player_mat_list.append(mat2)
                self.player_mat_list.draw()
                # Draw player cards
                if player.hole is not None:
                    card1 = player.hole[0]
                    card2 = player.hole[1]
                    arcade_card1 = ArcadePokerCard(card1, width=self.player_card_width)
                    arcade_card2 = ArcadePokerCard(card2, width=self.player_card_width)
                    arcade_card1.position = card_pos1
                    arcade_card2.position = card_pos2
                    self.player_card_list.append(arcade_card1)
                    self.player_card_list.append(arcade_card2)
                self.player_card_list.draw()
                # Draw player status
                bet = player_bets[i]
                status = player.status
                arcade.draw_text(
                    status,
                    card_pos1[0] - self.player_card_width / 2,
                    card_pos1[1] - self.player_card_height / 2 - self.margin,
                    arcade.color.BLACK,
                    self.default_font_size,
                    font_name=self.default_font,
                )
                arcade.draw_text(
                    f"$ {bet:.02f}",
                    betx,
                    bety,
                    arcade.color.BLACK,
                    self.default_font_size,
                    font_name=self.default_font,
                )
            else:
                # Draw empty seat
                arcade.draw_text(
                    "Empty",
                    card_pos1[0] - self.player_card_width / 2,
                    card_pos1[1] - self.player_card_height / 2 - self.margin / 2,
                    arcade.color.BLACK,
                    self.default_font_size,
                    font_name=self.default_font,
                )

        self.player_mat_list.draw()
        self.player_card_list.draw()

    def draw_board(self):
        self.board_mat_list = arcade.SpriteList()
        self.board_card_list = arcade.SpriteList()
        # Create the mats for the bottom face down and face up piles
        for i, board_card in enumerate(self.table.board):
            card_pos = self.index_to_board_card_cxcy[i]
            pile = arcade.SpriteSolidColor(
                self.board_card_width,
                self.board_card_height,
                arcade.csscolor.DARK_OLIVE_GREEN,
            )
            pile.position = card_pos
            self.board_mat_list.append(pile)

            if board_card is not None:
                arcade_card = ArcadePokerCard(board_card, width=self.board_card_width)
                arcade_card.position = card_pos
                self.board_card_list.append(arcade_card)

        self.board_mat_list.draw()
        self.board_card_list.draw()
        self.draw_button()
        self.draw_pot_size()

    def draw_button(self):
        bx, by = self.index_to_button_xy[self.table.button]
        radius = self.margin / 2
        arcade.draw_circle_filled(bx, by, radius, arcade.color.VANILLA)
        arcade.draw_text(
            "B",
            bx - radius / 2,
            by - radius / 2,
            color=arcade.color.BLACK,
            font_size=radius,
            bold=True,
        )

    def draw_pot_size(self):
        arcade.draw_text(
            f"Pot Size: ${self.table.get_pot_size():.02f} ({self.table.get_pot_size()/self.table.big_blind:.02f} BB)",
            self.width / 2,
            self.height / 2 + self.board_card_height / 2 + self.margin,
            color=arcade.color.BLACK,
            font_size=self.board_card_height / 6,
            bold=True,
            anchor_x="center",
        )

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        if self.table.finished():
            print("=====================================================")
            print(self.table.player_rankings_report()[1])
        else:
            self.table.play_hand()

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        pass

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
