import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, cast

import discord
from discord import Member
from PIL import Image, ImageDraw, ImageFont

from assets_caching import RARITY_CACHE
from economy.operations import get_shop
from firebase_client import db

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = BASE_DIR / "assets/fonts"

log.warning(f"BASE_DIR = {BASE_DIR}")
log.warning(f"ASSETS_DIR = {ASSETS_DIR} exists={ASSETS_DIR.exists()}")
log.warning(f"FONTS_DIR = {FONTS_DIR} exists={FONTS_DIR.exists()}")


async def generate_inventory(
    total_items: int,
    items: list,
    userId: str | None = None,
    page: int = 0,
    total_pages: int = 1,
) -> BytesIO:

    bg = Image.open(ASSETS_DIR / "inventory.png").convert("RGBA")

    font_small = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 26)
    font_light = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 26)
    font_bold = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 44)
    font_small_bold = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 32)

    draw = ImageDraw.Draw(bg)

    draw.text((57, 42), "Inventory", font=font_bold, fill="#FFFFFF")
    draw.text(
        (782, 688),
        f"Page {page + 1} / {total_pages}",
        font=font_small,
        fill="#FFFFFF",
    )
    draw.text(
        (57, 688),
        "Select the items you want to equip below.",
        font=font_light,
        fill="#FFFFFF",
    )

    x = 0
    y = 0
    gapX = 223
    gapY = 264

    quantity_image = Image.open(ASSETS_DIR / "quantity.png").convert("RGBA")
    quantity_image = quantity_image.resize((40, 35))
    bg.paste(
        quantity_image,
        (258, 58),
        quantity_image,
    )
    draw.text((268, 54), f"{total_items}", font=font_small_bold, fill="#FFFFFF")
    for item in items:
        image_path = ASSETS_DIR / item["display"]
        item_picture = Image.open(image_path).convert("RGBA")
        rarity = item.get("rarity", "common")
        rarity_image = RARITY_CACHE.get(rarity, None)
        if rarity_image:
            bg.paste(rarity_image, (207 + gapX * x, 337 + gapY * y), rarity_image)
        if x == 4:
            y += 1
            x = 0

        bg.paste(item_picture, (57 + gapX * x, 144 + gapY * y), item_picture)

        draw.text(
            (57 + gapX * x, 298 + gapY * y),
            item["id"],
            font=font_small,
            fill="#FFFFFF",
        )

        x += 1

    buffer = BytesIO()
    # bg.save("final_profile_card.png")
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
