import logging
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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
    gem_picture = gem_picture.resize((30, 30), Image.Resampling.LANCZOS)
    quantity_image = Image.open(ASSETS_DIR / "quantity.png").convert("RGBA")
    draw = ImageDraw.Draw(bg)
    draw.text(
        (57, 90),
        f"Page {page + 1} / {total_pages}",
        font=font_small,
        fill="#FFFFFF",
    )
    draw.text((57, 42), "Shop", font=font_bold, fill="#FFFFFF")
    draw.text((782, 47), f"{coins}", font=font_medium_bold, fill="#FFFFFF")
    draw.text(
        (57, 688),
        "Select the items you want to buy below.",
        font=font_light,
        fill="#FFFFFF",
    )
    x = 0
    y = 0
    gapX = 223
    gapY = 264
    for item in items:
        if x == 4:
            y += 1
            x = 0
        item_picture = Image.open(ASSETS_DIR / item["display"]).convert("RGBA")
        bg.paste(item_picture, (57 + gapX * x, 144 + gapY * y), item_picture)
        draw.text(
            (57 + gapX * x, 298 + gapY * y),
            f"{item['name']}",
            font=font_small,
            fill="#FFFFFF",
        )

        if item.get("currency", None) == "gems":
            bg.paste(gem_picture, (57 + gapX * x, 337 + gapY * y), gem_picture)
        else:
            bg.paste(coin_picture, (57 + gapX * x, 337 + gapY * y), coin_picture)
        bg.paste(quantity_image, (203 + gapX * x, 300 + gapY * y), quantity_image)
        draw.text(
            (88 + gapX * x, 334 + gapY * y),
            f"{item['price']}",
            font=font_light,
            fill="#FFFFFF",
        )
        quantity = item["quantity"]
        if quantity == -1:
            draw.text(
                (209 + gapX * x, 293 + gapY * y), f"∞", font=font_big, fill="#FFFFFF"
            )
        else:
            draw.text(
                (212 + gapX * x, 293 + gapY * y),
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
