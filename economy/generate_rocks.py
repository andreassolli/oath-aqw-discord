import random
from io import BytesIO
from pathlib import Path

from PIL import Image

from assets_caching import ROCKS_CACHE

ASSETS_DIR = Path(__file__).parent.parent / "assets"


def generate_rocks():
    bg = Image.open(ASSETS_DIR / "rocks.png").convert("RGBA")

    three_rocks = [random.choice(list(ROCKS_CACHE.items())) for _ in range(3)]

    bg.paste(three_rocks[0][1], (90, 54), three_rocks[0][1])
    bg.paste(three_rocks[1][1], (405, 54), three_rocks[1][1])
    bg.paste(three_rocks[2][1], (720, 54), three_rocks[2][1])

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer, [r[0] for r in three_rocks]
