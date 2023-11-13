import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ["PYOPENGL_PLATFORM"] = "osmesa"

import arcade

from pokerguac.poker_enginev2 import PokerGuacHoldemEngine


def main():
    """Main function"""
    game = PokerGuacHoldemEngine()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
