from io import BytesIO
from pathlib import Path

from PIL import Image

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def apply_extra_border(card_buffer: BytesIO, border: str) -> BytesIO:
    card_buffer.seek(0)
    card = Image.open(card_buffer).convert("RGBA")

    border_image = Image.open(ASSETS_DIR / f"{border}").convert("RGBA")

    # Create canvas = hand size
    canvas = Image.new("RGBA", (border_image.width, border_image.height), (0, 0, 0, 0))

    card_x = (border_image.width - card.width) // 2
    card_y = 101

    canvas.paste(card, (card_x, card_y), card)

    # Hand on top
    canvas.paste(border_image, (0, 0), border_image)

    out = BytesIO()
    canvas.save(out, format="PNG")
    out.seek(0)

    return out
