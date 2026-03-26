import asyncio
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, cast

from discord import Member
from PIL import Image, ImageDraw, ImageFont

from config import POTW_ROLE_ID
from firebase_client import db

from .utils import circle_crop, fetch_avatar, ordinal, sort_badges

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = BASE_DIR / "assets/fonts"


def load_asset(name, size=None):
    img = Image.open(ASSETS_DIR / name).convert("RGBA")
    if size:
        img = img.resize(size, Image.Resampling.LANCZOS)
    return img


def load_font(name, size):
    return ImageFont.truetype(FONTS_DIR / name, size)


BADGE_TO_IMAGE = {
    "Beta Tester1": ASSETS_DIR / "beta_tester1.png",
    "Beta Tester2": ASSETS_DIR / "beta_tester2.png",
    "Beta Tester3": ASSETS_DIR / "beta_tester3.png",
    "Guild Founder": ASSETS_DIR / "oathfounder.png",
    "AQW Founder": ASSETS_DIR / "founderaqw.png",
    "Achievement Badges I": ASSETS_DIR / "aqwbadges1.png",
    "Achievement Badges II": ASSETS_DIR / "aqwbadges2.png",
    "Achievement Badges III": ASSETS_DIR / "aqwbadges3.png",
    "Achievement Badges IV": ASSETS_DIR / "aqwbadges4.png",
    "Epic Journey I": ASSETS_DIR / "epic1.png",
    "Epic Journey II": ASSETS_DIR / "epic2.png",
    "Epic Journey III": ASSETS_DIR / "epic3.png",
    "Epic Journey IV": ASSETS_DIR / "epic4.png",
    "Class Collector I": ASSETS_DIR / "class1.png",
    "Class Collector II": ASSETS_DIR / "class2.png",
    "Class Collector III": ASSETS_DIR / "class3.png",
    "Class Collector IV": ASSETS_DIR / "class4.png",
    "51% Weapons I": ASSETS_DIR / "weapon1.png",
    "51% Weapons II": ASSETS_DIR / "weapon2.png",
    "51% Weapons III": ASSETS_DIR / "weapon3.png",
    "51% Weapons IV": ASSETS_DIR / "weapon4.png",
    "Whale I": ASSETS_DIR / "whale1.webp",
    "Whale II": ASSETS_DIR / "whale2.webp",
    "Whale III": ASSETS_DIR / "whale3.webp",
    "Whale IV": ASSETS_DIR / "whale4.webp",
}


async def generate_test_card(
    # interaction,
    # target: Member,
) -> tuple[BytesIO, list[str], bool, bool, str, int]:
    # user_id = target.id
    # server_id = interaction.guild.id

    # mee6_task = fetch_mee6_stats(user_id, server_id)
    # avatar_task = fetch_avatar(target.display_avatar.url)

    # mee6, avatar = await asyncio.gather(mee6_task, avatar_task)

    doc_ref = db.collection("users").document(str(292040660696039424))

    doc = cast(Any, doc_ref.get())
    data: Dict[str, Any] = doc.to_dict() or {}

    badges = sort_badges(data.get("badges", []))
    points = data.get("points", 0)
    tickets_claimed = data.get("tickets_claimed", 0)
    guild = str(data.get("guild", "No guild"))
    if guild == "None":
        guild = "No guild"
    has_been_potw = data.get("has_been_potw", False)
    # is_potw = any(role.id == POTW_ROLE_ID for role in target.roles)
    game_ref = db.collection("wordle_games").document(str(292040660696039424))
    game_doc = game_ref.get()
    game_data = game_doc.to_dict() if game_doc.exists else {}
    completed_words = game_data.get("words_completed", 0)
    users_above = list(db.collection("users").where("points", ">", points).stream())
    rank = len(users_above) + 1
    coins = data.get("coins", 0)
    wins = data.get("wins", 0)
    border = data.get("border", {})
    card = data.get("card", {})
    gems = data.get("gems", 0)
    bg = Image.open(ASSETS_DIR / f"test_profile2.png").convert("RGBA")

    # if border:
    #    border_img = Image.open(ASSETS_DIR / f"{border.get('image')}").convert("RGBA")
    #    bg.paste(border_img, (0, 0), border_img)

    draw = ImageDraw.Draw(bg)
    # avatar = circle_crop(avatar, 231)
    # bg.paste(avatar, (44, 32), avatar)

    # if border == "Test Border":
    #    test_border = Image.open(ASSETS_DIR / "test_border.png").convert("RGBA")
    #    bg.paste(test_border, (0, 0), test_border)
    # if is_potw:
    #    potw_border = ASSET_CACHE["potw_border"]
    #    bg.paste(potw_border, (27, 19), potw_border)

    font_big = load_font("Urbanist-Regular.ttf", 54)
    font_bold = load_font("Urbanist-Bold.ttf", 66)
    font_light = load_font("Urbanist-Light.ttf", 24)
    font_small = load_font("Urbanist-Regular.ttf", 30)
    font_xsmall = load_font("Urbanist-Regular.ttf", 24)
    font_xsmall_light = load_font("Urbanist-Light.ttf", 21)

    draw.text((316, 32), "Proxy", font=font_big, fill="#FFFFFF")
    if has_been_potw:
        name = "Proxy"
        name_x = 316
        name_y = 32

        # Measure text width
        bbox = draw.textbbox((0, 0), name, font=font_big)
        text_width = bbox[2] - bbox[0]

        # Padding between name and flare
        padding = 9

        flare_x = int(name_x + text_width + padding)
        flare_y = int(name_y + padding)

        potw_flare = load_asset("potw_flare.webp", (42, 42))
        bg.paste(potw_flare, (flare_x, flare_y), potw_flare)
    draw.text((316, 92), guild, font=font_small, fill="#FFFFFF")

    joined_text = "Joined unknown"

    draw.text(
        (316, 144),
        joined_text,
        font=font_light,
        fill="#FFFFFF",
    )

    # draw.text((44, 285), "Badges", font=font_small, fill="#FFFFFF")

    # draw.text((322, 200), "Stats", font=font_small, fill="#FFFFFF")

    draw.text((349, 193), str(100), font=font_bold, fill="#FFFFFF")

    draw.text((326, 233), "lvl", font=font_xsmall, fill="#FFFFFF")

    draw.text(
        (326, 260),
        f"1234 / 2345 xp",
        font=font_xsmall_light,
        fill="#FFFFFF",
    )

    draw.text((529, 210), f"1112 messages", font=font_xsmall, fill="#FFFFFF")

    draw.text(
        (529, 255), f"AQWordle: {completed_words}", font=font_xsmall, fill="#FFFFFF"
    )

    # draw.text((322, 375), "Misc", font=font_small, fill="#FFFFFF")

    draw.text((354, 324), f"{gems}", font=font_xsmall, fill="#FFFFFF")

    draw.text((354, 371), f"{points} points", font=font_xsmall, fill="#FFFFFF")

    draw.text((529, 324), f"{coins}", font=font_xsmall, fill="#FFFFFF")

    draw.text(
        (529, 371),
        f"{ordinal(rank)} place",
        font=font_xsmall,
        fill="#FFFFFF",
    )

    trophy = load_asset("coin.png", (27, 27))
    calendar = load_asset("calendar.png", (27, 27))
    gem = load_asset("gem.png", (27, 27))
    medal = load_asset("medal.png", (27, 27))
    dice = load_asset("dice.png", (27, 27))
    messages = load_asset("messages.png", (27, 27))

    x = 0
    y = 0
    for badge in badges:
        if badge in BADGE_TO_IMAGE:
            badge_img = Image.open(BADGE_TO_IMAGE[badge]).convert("RGBA")
            badge_img = badge_img.resize((69, 69), Image.Resampling.LANCZOS)
            if x == 3:
                y += 1
                x = 0
            bg.paste(badge_img, (45 + 81 * x, 291 + 81 * y), badge_img)
            x += 1
    # bg.paste(forge, (29, 224), forge)
    # bg.paste(sword, (73, 224), sword)

    bg.paste(trophy, (491, 327), trophy)
    bg.paste(calendar, (491, 372), calendar)
    bg.paste(gem, (319, 327), gem)
    bg.paste(medal, (319, 374), medal)
    bg.paste(messages, (491, 212), messages)
    bg.paste(dice, (491, 257), dice)

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    bg.save("test_image.png", format="PNG")
    buffer.seek(0)

    return buffer, badges, False, has_been_potw, "Proxy", wins
