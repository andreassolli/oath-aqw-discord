import logging
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from assets_caching import RARITY_CACHE
from firebase_client import db

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = BASE_DIR / "assets/fonts"

log.warning(f"BASE_DIR = {BASE_DIR}")
log.warning(f"ASSETS_DIR = {ASSETS_DIR} exists={ASSETS_DIR.exists()}")
log.warning(f"FONTS_DIR = {FONTS_DIR} exists={FONTS_DIR.exists()}")


async def generate_shop(
    items: list,
    userId: str | None = None,
    page: int = 0,
    min_price: int | None = None,
    max_price: int | None = None,
    total_pages: int = 1,
) -> BytesIO:

    user_doc = db.collection("users").document(userId).get()
    coins = (user_doc.to_dict() or {}).get("coins", 0)
    gems = (user_doc.to_dict() or {}).get("gems", 0)
    bg = Image.open(ASSETS_DIR / "shop.png").convert("RGBA")
    font_big = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 34)
    font_not_as_big = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 30)
    font_medium_bold = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 36)
    font_bold = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 44)
    font_light = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 26)
    font_small = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 24)
    font_xsmall = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 20)
    font_xsmall_light = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 14)
    coin_picture = Image.open(ASSETS_DIR / "coin.png").convert("RGBA")
    coin_picture = coin_picture.resize((27, 30), Image.Resampling.LANCZOS)
    gem_picture = Image.open(ASSETS_DIR / "gem.png").convert("RGBA")
    gem_picture_buy = gem_picture.resize((30, 30), Image.Resampling.LANCZOS)
    gem_picture_inv = gem_picture.resize((37, 37), Image.Resampling.LANCZOS)
    quantity_image = Image.open(ASSETS_DIR / "quantity.png").convert("RGBA")

    draw = ImageDraw.Draw(bg)
    draw.text(
        (847, 688),
        f"Page {page + 1} / {total_pages}",
        font=font_small,
        fill="#FFFFFF",
    )
    draw.text((57, 42), "Shop", font=font_bold, fill="#FFFFFF")
    draw.text((663, 47), f"{coins}", font=font_medium_bold, fill="#FFFFFF")
    bg.paste(gem_picture_inv, (800, 50), gem_picture_inv)
    draw.text((842, 47), f"{gems}", font=font_medium_bold, fill="#FFFFFF")
    draw.text(
        (57, 688),
        "Select the items you want to buy below.",
        font=font_light,
        fill="#FFFFFF",
    )
    x = 0
    y = 0
    gapX = 240
    gapY = 264
    for item in items:
        if x == 4:
            y += 1
            x = 0
        rarity = item.get("rarity", "common")
        rarity_image = RARITY_CACHE.get(rarity, None)
        if rarity_image:
            bg.paste(rarity_image, (207 + gapX * x, 298 + gapY * y), rarity_image)
        item_picture = Image.open(ASSETS_DIR / item["display"]).convert("RGBA")
        bg.paste(item_picture, (57 + gapX * x, 144 + gapY * y), item_picture)
        draw.text(
            (57 + gapX * x, 298 + gapY * y),
            f"{item['name']}",
            font=font_small,
            fill="#FFFFFF",
        )

        shard_price = item.get("shard_price", 0)
        coin_price = item.get("coin_price", 0)
        has_coins = coin_price > 0
        has_shards = shard_price > 0
        has_coins = coin_price > 0
        has_shards = shard_price > 0

        # Coins
        if has_coins:
            bg.paste(coin_picture, (57 + gapX * x, 337 + gapY * y), coin_picture)
            draw.text(
                (88 + gapX * x, 334 + gapY * y),
                f"{coin_price}",
                font=font_light,
                fill="#FFFFFF",
            )

        # Shards
        if has_shards:
            offset = 180 if has_coins else 57

            bg.paste(
                gem_picture_buy,
                (offset + gapX * x, 334 + gapY * y),
                gem_picture_buy,
            )
            draw.text(
                (offset + 30 + gapX * x, 334 + gapY * y),
                f"{shard_price}",
                font=font_light,
                fill="#FFFFFF",
            )

        bg.paste(quantity_image, (203 + gapX * x, 144 + gapY * y), quantity_image)
        first_price = coin_price if coin_price != 0 else shard_price
        draw.text(
            (88 + gapX * x, 334 + gapY * y),
            f"{first_price}",
            font=font_light,
            fill="#FFFFFF",
        )
        quantity = item["quantity"]
        if quantity == -1:
            draw.text(
                (209 + gapX * x, 138 + gapY * y), f"∞", font=font_big, fill="#FFFFFF"
            )
        else:
            draw.text(
                (212 + gapX * x, 134 + gapY * y),
                f"{quantity}",
                font=font_big,
                fill="#FFFFFF",
            )

        x += 1

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    # bg.save("final_profile_card.png")
    buffer.seek(0)

    return buffer
