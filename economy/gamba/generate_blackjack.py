from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .utils import rounded_crop

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


async def generate_blackjack(user_cards, dealer_cards, dealer_faceup: bool = False):
    bg = Image.open(ASSETS_DIR / "blackjack.png").convert("RGBA")
    # draw = ImageDraw.Draw(bg)
    card = Image.open(ASSETS_DIR / "cardback.png").convert("RGBA")
    card = card.resize((108, 171))

    for i, user_card in enumerate(user_cards):
        card_path = ASSETS_DIR / f"{NUM_MAP[user_card[1]]}{SUIT_MAP[user_card[0]]}.png"
        card_image = Image.open(card_path).convert("RGBA")
        card_image = rounded_crop(card_image, 104, 169, 22)
        bg.paste(card_image, (58 + i * 117, 254), card_image)

    for i in range(0, len(dealer_cards)):
        if dealer_faceup:
            card_path = (
                ASSETS_DIR
                / f"{NUM_MAP[dealer_cards[i][1]]}{SUIT_MAP[dealer_cards[i][0]]}.png"
            )
            card_image = Image.open(card_path).convert("RGBA")
            card_image = rounded_crop(card_image, 104, 169, 22)
            bg.paste(card_image, (58 + i * 117, 52), card_image)
        else:
            bg.paste(card, (58 + i * 117, 52), card)

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    # bg.save("blackjack.png", format="PNG")
    buffer.seek(0)

    return buffer
