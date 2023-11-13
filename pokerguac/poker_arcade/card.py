import arcade
from os.path import exists as path_exists
from ..poker.components import PokerCard
from typing import Optional, Tuple
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

    @classmethod
    def get_size(cls, card_width: float) -> Tuple[int, int]:
        """
        Returns
        -------
        (h, w): card size preserving card img file width height ratio
        """
        back_image = f"./assets/poker_deck/back.png"
        assert path_exists(back_image), f"{back_image} does not exist!"
        im_w, im_h = Image.open(back_image).size
        scale = card_width / im_w
        card_w = round(im_w * scale)
        card_h = round(im_h * scale)
        return (card_h, card_w)
