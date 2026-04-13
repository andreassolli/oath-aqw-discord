from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"


async def generate_blackjack(user_cards, dealer_cards):
    bg = Image.open(ASSETS_DIR / "blackjack.png").convert("RGBA")
    # draw = ImageDraw.Draw(bg)
    card = Image.open(ASSETS_DIR / "cardback.png").convert("RGBA")
    card = card.resize((108, 171))

    for i in range(0, len(user_cards)):
        bg.paste(card, (65 + i * 117, 74), card)

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    # bg.save("blackjack.png", format="PNG")
    buffer.seek(0)

    return buffer
