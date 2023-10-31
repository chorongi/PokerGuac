import arcade
from ..poker.components import PokerCard
from typing import Optional
from PIL import Image


class ArcadePokerCard(arcade.Sprite):
    """Card sprite"""

    card: PokerCard
    width: float
    height: float

    def __init__(self, card: PokerCard, width: Optional[float] = None):
        """Card constructor"""

        # Attributes for suit and value
        self.card = card

        # Image to use for the sprite when face up
        self.front_image = f"./assets/poker_deck/{self.card}.png"
        im_w, im_h = Image.open(self.front_image).size
        scale = width / im_w if width is not None else 1
        self._width = im_w * scale
        self._height = im_h * scale

        # Call the parent
        super().__init__(self.front_image, scale, hit_box_algorithm="None")
