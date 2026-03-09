import datetime
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, cast

import discord
from discord import Member
from PIL import Image, ImageDraw, ImageFont

from firebase_client import db
from user_profile.utils import circle_crop, fetch_avatar

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = BASE_DIR / "assets/fonts"

log.warning(f"BASE_DIR = {BASE_DIR}")
log.warning(f"ASSETS_DIR = {ASSETS_DIR} exists={ASSETS_DIR.exists()}")
log.warning(f"FONTS_DIR = {FONTS_DIR} exists={FONTS_DIR.exists()}")

FIELD_TO_IMAGE = {
    "wrong": ASSETS_DIR / "wrong.png",
    "partially": ASSETS_DIR / "partial.png",
    "correct": ASSETS_DIR / "correct.png",
}

KEYBOARD_ROWS = [
    "QWERTYUIOP",
    "ASDFGHJKL",
    "ZXCVBNM",
]


async def generate_wordle_share(interaction: discord.Interaction) -> BytesIO:
    bg = Image.open(ASSETS_DIR / "aqwordle_shared.png").convert("RGBA")
    draw = ImageDraw.Draw(bg)

    userId = str(interaction.user.id)
    game_ref = db.collection("wordle_games").document(userId)
    game_doc = game_ref.get()
    game_data = game_doc.to_dict() if game_doc.exists else {}
    avatar = await fetch_avatar(interaction.user.display_avatar.url)
    avatar = circle_crop(avatar, 231)
    bg.paste(avatar, (30, 25), avatar)
    guesses = game_data.get("guesses", [])
    # Tile layout
    start_x = 308
    start_y = 49
    tile_size = 51
    x_spacing = 9
    y_spacing = 9
    title_font = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 32)
    date_font = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 32)
    credit_font = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 20)
    draw.text((64, 276), "AQWordle", font=title_font, fill="#FFFFFF")
    todays_date = datetime.date.today().strftime("%Y-%m-%d")
    draw.text((56, 316), todays_date, font=date_font, fill="#FFFFFF")
    draw.text((100, 390), "by Oath", font=credit_font, fill="#FFFFFF")
    for row_index, guess_data in enumerate(guesses[:6]):
        if isinstance(guess_data, dict):
            pattern = guess_data["pattern"].split(" ")

        else:
            # Old format fallback
            pattern = guess_data.split(" ")

        for col_index in range(5):
            state_emoji = pattern[col_index]

            if state_emoji == "🟩":
                tile_img = Image.open(FIELD_TO_IMAGE["correct"]).convert("RGBA")
            elif state_emoji == "🟨":
                tile_img = Image.open(FIELD_TO_IMAGE["partially"]).convert("RGBA")
            else:
                tile_img = Image.open(FIELD_TO_IMAGE["wrong"]).convert("RGBA")

            x = start_x + col_index * (tile_size + x_spacing)
            y = start_y + row_index * (tile_size + y_spacing)

            tile_img = tile_img.resize((tile_size, tile_size))
            bg.paste(tile_img, (x, y), tile_img)

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
