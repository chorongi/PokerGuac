import arcade
import arcade.gui
from uuid import uuid5
from .buttons import QuitButton


class PokerHomeScreen(arcade.View):
    default_font_size: int = 9
    default_font: str = "Arial"

    def __init__(self, window: arcade.Window):
        super().__init__(window)  # type: ignore (hkwark)
        arcade.set_background_color(arcade.color.AMAZON)  # type: ignore (hkwark)
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        start_game_button = arcade.gui.UIFlatButton(
            text="Start Game", width=self.window.width / 20
        )
        exit_game_button = QuitButton()
        start_game_button.on_click = self.start_game
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", child=start_game_button
            )
        )

    def start_game(self, event):
        print("Start:", event)

    def setup(self):
        """Set up the game variables. Call to re-start the game."""
        # Create your sprites and sprite lists here

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()
        # Call draw() on all your sprite lists below
        self.manager.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        pass

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
