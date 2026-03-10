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


async def generate_wordle_board(
    interaction: discord.Interaction | None = None, userId: str | None = None
) -> BytesIO:
    bg = Image.open(ASSETS_DIR / "aqwordle.png").convert("RGBA")
    draw = ImageDraw.Draw(bg)

    userId = userId if userId else str(interaction.user.id)
    game_ref = db.collection("wordle_games").document(userId)
    game_doc = game_ref.get()
    game_data = game_doc.to_dict() if game_doc.exists else {}

    guesses = game_data.get("guesses", [])
    letter_states = game_data.get("letter_states", {})
    # Tile layout
    start_x = 52
    start_y = 112
    tile_size = 51
    x_spacing = 9
    y_spacing = 9
    title_font = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 32)
    draw.text((120, 34), "AQWordle", font=title_font, fill="#FFFFFF")
    font = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 32)

    for row_index, guess_data in enumerate(guesses[:6]):
        if isinstance(guess_data, dict):
            pattern = guess_data["pattern"].split(" ")
            word = guess_data["guess"].upper()
        else:
            # Old format fallback
            pattern = guess_data.split(" ")
            word = "WRATH"  # You don't have the word stored in old format

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

            # Draw letter
            letter = word[col_index]
            text_bbox = draw.textbbox((0, 0), letter, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]

            draw.text(
                (
                    x + (tile_size - (text_w + 1)) / 2,
                    y + (tile_size - text_h * 1.75) / 2,
                ),
                letter,
                font=font,
                fill="white",
            )
        # 🔤 Draw Keyboard
        keyboard_start_y = 500
        keyboard_start_x = 72
        key_spacing_x = 28
        key_spacing_y = 28

        keyboard_font = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 22)

        for row_index, row in enumerate(KEYBOARD_ROWS):
            if row_index == 1:
                x_loc = keyboard_start_x + 14
            elif row_index == 2:
                x_loc = keyboard_start_x + 34
            else:
                x_loc = keyboard_start_x
            for col_index, char in enumerate(row):
                x = x_loc + col_index * key_spacing_x
                y = keyboard_start_y + row_index * key_spacing_y

                state = letter_states.get(char.lower())

                # Gray out ONLY wrong letters
                if state == "wrong":
                    color = (115, 115, 115)  # gray
                else:
                    color = (255, 255, 255)  # white

                text_bbox = draw.textbbox((0, 0), char, font=keyboard_font)
                text_w = text_bbox[2] - text_bbox[0]
                text_h = text_bbox[3] - text_bbox[1]

                draw.text(
                    (x - text_w / 2, y - text_h / 2),
                    char,
                    font=keyboard_font,
                    fill=color,
                )
    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
