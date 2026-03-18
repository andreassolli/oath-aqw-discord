from io import BytesIO
from pathlib import Path

from PIL import Image

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def apply_hand_overlay(card_buffer: BytesIO) -> BytesIO:
    card_buffer.seek(0)
    card = Image.open(card_buffer).convert("RGBA")

    hand = Image.open(ASSETS_DIR / "hand_test2.png").convert("RGBA")

    # Create canvas = hand size
    canvas = Image.new("RGBA", (card.width, hand.height), (0, 0, 0, 0))

    # 🎯 Position card (centered horizontally, slightly up)
    card_x = (hand.width - card.width) // 2
    card_y = 106

    canvas.paste(card, (card_x, card_y), card)

    # Hand on top
    canvas.paste(hand, (0, 0), hand)

    out = BytesIO()
    canvas.save(out, format="PNG")
    out.seek(0)

    return out
