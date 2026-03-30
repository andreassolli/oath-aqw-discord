import random
from io import BytesIO
from pathlib import Path

from PIL import Image

from assets_caching import ROCKS_CACHE

ASSETS_DIR = Path(__file__).parent.parent / "assets"


def generate_rocks():
    bg = Image.open(ASSETS_DIR / "rock_background.png").convert("RGBA")

    valid_rocks = [(k, v) for k, v in ROCKS_CACHE.items() if 1 <= k <= 9]
    three_rocks = [random.choice(valid_rocks) for _ in range(3)]

    positions = [(84, 83), (404, 83), (724, 83)]

    for i, (rock_id, rock_img) in enumerate(three_rocks):
        bg.paste(rock_img, positions[i], rock_img)

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer, [r[0] for r in three_rocks]


def generate_rocks_from_ids(rock_ids: list[int]):
    bg = Image.open(ASSETS_DIR / "rock_background.png").convert("RGBA")

    positions = [(84, 83), (404, 83), (724, 83)]

    for i, rock_id in enumerate(rock_ids):
        rock_img = ROCKS_CACHE[rock_id]
        bg.paste(rock_img, positions[i], rock_img)

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
