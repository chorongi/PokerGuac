import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ["PYOPENGL_PLATFORM"] = "osmesa"
# os.environ["PYOPENGL_PLATFORM"] = "egl"

import arcade

from pokerguac.poker_engine import PokerGuacEngine

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"


def main():
    """Main function"""
    game = PokerGuacEngine(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
