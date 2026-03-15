import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, cast

import discord
from discord import Member
from PIL import Image, ImageDraw, ImageFont

from economy.operations import get_shop
from firebase_client import db

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = BASE_DIR / "assets/fonts"

log.warning(f"BASE_DIR = {BASE_DIR}")
log.warning(f"ASSETS_DIR = {ASSETS_DIR} exists={ASSETS_DIR.exists()}")
log.warning(f"FONTS_DIR = {FONTS_DIR} exists={FONTS_DIR.exists()}")


async def generate_shop(
    interaction: discord.Interaction | None = None, userId: str | None = None
) -> BytesIO:
    items = await get_shop()
    user_doc = db.collection("users").document(userId).get()
    coins = (user_doc.to_dict() or {}).get("coins", 0)
    bg = Image.open(ASSETS_DIR / "shop.png").convert("RGBA")
    font_big = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 34)
    font_medium_bold = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 36)
    font_bold = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 44)
    font_light = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 26)
    font_small = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 26)
    font_xsmall = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 20)
    font_xsmall_light = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 14)
    draw = ImageDraw.Draw(bg)

    draw.text((57, 42), "Shop", font=font_bold, fill="#FFFFFF")
    draw.text((782, 47), f"{coins}", font=font_medium_bold, fill="#FFFFFF")

    x = 0
    y = 0
    for item in items:
        if x == 4:
            y += 1
            x = 0
        item_picture = Image.open(ASSETS_DIR / item["image"]).convert("RGBA")
        bg.paste(item_picture, (57 + 28 * x, 144 + 28 * y))
        draw.text((57, 298), f"{item['name']}", font=font_small, fill="#FFFFFF")
        coin_picture = Image.open(ASSETS_DIR / "coin.png").convert("RGBA")
        bg.paste(coin_picture, (57, 328))
        draw.text((94, 328), f"{item['price']}", font=font_light, fill="#FFFFFF")
        quantity = item["quantity"]
        if quantity == -1:
            draw.text((209, 293), f"∞", font=font_big, fill="#FFFFFF")
        else:
            draw.text((209, 293), f"{quantity}", font=font_big, fill="#FFFFFF")

        x += 1

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    bg.save("final_profile_card.png")
    buffer.seek(0)

    return buffer
