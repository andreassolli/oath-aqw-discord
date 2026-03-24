import random
from io import BytesIO
from pathlib import Path

from PIL import Image

from assets_caching import ROCKS_CACHE

ASSETS_DIR = Path(__file__).parent.parent / "assets"


def generate_rocks():
    bg = Image.open(ASSETS_DIR / "rocks.png").convert("RGBA")

    three_rocks = [
        random.choice(list(ROCKS_CACHE.items()))  # (key, image)
        for _ in range(3)
    ]

    processed = []
    for key, img in three_rocks:
        processed.append((key, img.copy().resize((225, 225))))

    bg.paste(processed[0][1], (90, 0), processed[0][1])
    bg.paste(processed[1][1], (315, 0), processed[1][1])
    bg.paste(processed[2][1], (530, 0), processed[2][1])

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    # return BOTH image + rock types
    return buffer, [r[0] for r in processed]
