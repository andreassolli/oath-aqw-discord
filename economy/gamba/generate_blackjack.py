from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from assets_caching import CARD_CACHE

from .utils import rounded_card_crop

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"

NUM_MAP = {
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "10",
    11: "J",
    12: "Q",
    13: "K",
    14: "A",
}

SUIT_MAP = {
    1: "D",
    2: "H",
    3: "C",
    4: "S",
}

BG = CARD_CACHE["blackjack"]
# draw = ImageDraw.Draw(bg)
CARD_BACK = CARD_CACHE["cardback"]


async def generate_blackjack(user_cards, dealer_cards, dealer_faceup: bool = False):
    bg = BG.copy()
    card = CARD_CACHE["cardback"]

    for i, user_card in enumerate(user_cards):
        card_image = CARD_CACHE[user_card]
        bg.paste(card_image, (58 + i * 117, 254), card_image)

    for i in range(0, len(dealer_cards)):
        if dealer_faceup:
            card_image = CARD_CACHE[dealer_cards[i]]
            bg.paste(card_image, (58 + i * 117, 52), card_image)
        else:
            bg.paste(card, (58 + i * 117, 52), card)

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    # bg.save("blackjack.png", format="PNG")
    buffer.seek(0)

    return buffer
