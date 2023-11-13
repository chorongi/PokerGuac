import arcade
import numpy as np

from .poker_arcade import PokerHomeScreen, PokerTableScreen
from .poker.agents import ALL_AGENT_TYPES
from .poker.components.constants import MAX_NUM_PLAYERS
from .poker import poker_cache_game_init, poker_tournament_init
from .poker_arcade.constants import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE


class PokerGuacHoldemEngine(arcade.Window):
    current_screen: arcade.View

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)  # type: ignore hkwark
        self.setup()
        self.home_screen = PokerHomeScreen(self)
        self.table_screen = PokerTableScreen(self, self.table)
        self.current_screen = self.table_screen

    def setup(self):
        """Set up the game variables. Call to re-start the game."""
        # Create your sprites and sprite lists here
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
            np.random.choice(ALL_AGENT_TYPES, MAX_NUM_PLAYERS, replace=True)
        )
        self.table, _ = poker_tournament_init(
            player_names, action_agent_types, MAX_NUM_PLAYERS
        )

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()
        # Call draw() on all your sprite lists below
        self.current_screen.on_draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.current_screen.on_update(delta_time)

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        self.current_screen.on_key_press(key, key_modifiers)

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        self.current_screen.on_key_release(key, key_modifiers)

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
        self.current_screen.on_mouse_release(x, y, button, key_modifiers)
