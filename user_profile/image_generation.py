import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, cast

from discord import Member
from PIL import Image, ImageDraw, ImageFont

from config import POTW_ROLE_ID
from firebase_client import db

from .mee6_fetcher import fetch_mee6_stats
from .utils import circle_crop, fetch_avatar, ordinal, sort_badges

log = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = BASE_DIR / "assets/fonts"

log.warning(f"BASE_DIR = {BASE_DIR}")
log.warning(f"ASSETS_DIR = {ASSETS_DIR} exists={ASSETS_DIR.exists()}")
log.warning(f"FONTS_DIR = {FONTS_DIR} exists={FONTS_DIR.exists()}")

BADGE_TO_IMAGE = {
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


async def generate_profile_card(
    interaction,
    target: Member,
) -> tuple[BytesIO, list[str], bool, bool, str, int]:
    user_id = target.id
    server_id = interaction.guild.id
    mee6 = await fetch_mee6_stats(user_id, server_id)

    doc_ref = db.collection("users").document(str(user_id))

    doc = cast(Any, doc_ref.get())
    data: Dict[str, Any] = doc.to_dict() or {}

    badges = sort_badges(data.get("badges", []))
    points = data.get("points", 0)
    tickets_claimed = data.get("tickets_claimed", 0)
    guild = str(data.get("guild", "No guild"))
    has_been_potw = data.get("has_been_potw", False)
    users_above = db.collection("users").where("points", ">", points).stream()
    is_potw = any(role.id == POTW_ROLE_ID for role in target.roles)
    game_ref = db.collection("wordle_games").document(str(target.id))
    game_doc = game_ref.get()
    game_data = game_doc.to_dict() if game_doc.exists else {}
    completed_words = game_data.get("words_completed", 0)
    rank = sum(1 for _ in users_above) + 1
    wins = data.get("wins", 0)
    border = data.get("border", "")
    card = data.get("card", "")
    if card:
        bg = Image.open(ASSETS_DIR / f"{card['image']}.png").convert("RGBA")
    else:
        bg = Image.open(ASSETS_DIR / "card.png").convert("RGBA")
    draw = ImageDraw.Draw(bg)
    avatar = await fetch_avatar(target.display_avatar.url)
    avatar = circle_crop(avatar, 231)
    bg.paste(avatar, (44, 32), avatar)

    # if border == "Test Border":
    #    test_border = Image.open(ASSETS_DIR / "test_border.png").convert("RGBA")
    #    bg.paste(test_border, (0, 0), test_border)
    if is_potw:
        potw_border = Image.open(ASSETS_DIR / "potw_border.webp").convert("RGBA")
        potw_border = potw_border.resize((158, 168), Image.Resampling.LANCZOS)
        bg.paste(potw_border, (27, 19), potw_border)

    font_big = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 54)
    font_bold = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 66)
    font_light = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 24)
    font_small = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 30)
    font_xsmall = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 24)
    font_xsmall_light = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 21)

    draw.text((340, 32), target.display_name, font=font_big, fill="#FFFFFF")
    if has_been_potw:
        name = target.display_name
        name_x = 340
        name_y = 32

        # Measure text width
        bbox = draw.textbbox((0, 0), name, font=font_big)
        text_width = bbox[2] - bbox[0]

        # Padding between name and flare
        padding = 9

        flare_x = int(name_x + text_width + padding)
        flare_y = int(name_y + padding)

        potw_flare = Image.open(ASSETS_DIR / "potw_flare.webp").convert("RGBA")
        potw_flare = potw_flare.resize((42, 42), Image.Resampling.LANCZOS)
        bg.paste(potw_flare, (flare_x, flare_y), potw_flare)
    draw.text((340, 92), guild, font=font_small, fill="#FFFFFF")

    if target.joined_at:
        day = target.joined_at.day
        joined_text = f"Joined {day}. {target.joined_at.strftime('%b %Y')}"
    else:
        joined_text = "Joined unknown"

    draw.text(
        (340, 144),
        joined_text,
        font=font_light,
        fill="#FFFFFF",
    )

    draw.text((44, 285), "Badges", font=font_small, fill="#FFFFFF")

    draw.text((356, 200), "Stats", font=font_small, fill="#FFFFFF")

    draw.text((383, 233), str(mee6["level"]), font=font_bold, fill="#FFFFFF")

    draw.text((360, 273), "lvl", font=font_xsmall, fill="#FFFFFF")

    draw.text(
        (360, 300),
        f"{mee6['current_xp']} / {mee6['xp_to_level']} xp",
        font=font_xsmall_light,
        fill="#FFFFFF",
    )

    draw.text((563, 248), f"{mee6['messages']} sent", font=font_xsmall, fill="#FFFFFF")

    draw.text(
        (563, 293), f"Wordle: {completed_words}", font=font_xsmall, fill="#FFFFFF"
    )

    draw.text((356, 375), "Tickets", font=font_small, fill="#FFFFFF")

    draw.text((401, 420), f"{tickets_claimed} helped", font=font_xsmall, fill="#FFFFFF")

    draw.text((401, 467), f"{points} points", font=font_xsmall, fill="#FFFFFF")

    draw.text((563, 420), f"{wins} wins", font=font_xsmall, fill="#FFFFFF")

    draw.text(
        (563, 467),
        f"{ordinal(rank)} place",
        font=font_xsmall,
        fill="#FFFFFF",
    )

    trophy = Image.open(ASSETS_DIR / "trophy.png").convert("RGBA")
    trophy = trophy.resize((27, 27), Image.Resampling.LANCZOS)
    calendar = Image.open(ASSETS_DIR / "calendar.png").convert("RGBA")
    calendar = calendar.resize((27, 27), Image.Resampling.LANCZOS)
    ticket = Image.open(ASSETS_DIR / "ticket.png").convert("RGBA")
    ticket = ticket.resize((27, 27), Image.Resampling.LANCZOS)
    medal = Image.open(ASSETS_DIR / "medal.png").convert("RGBA")
    medal = medal.resize((27, 27), Image.Resampling.LANCZOS)
    dice = Image.open(ASSETS_DIR / "dice.png").convert("RGBA")
    dice = dice.resize((27, 27), Image.Resampling.LANCZOS)
    messages = Image.open(ASSETS_DIR / "messages.png").convert("RGBA")
    messages = messages.resize((27, 27), Image.Resampling.LANCZOS)
    forge = Image.open(ASSETS_DIR / "forge.png").convert("RGBA")
    forge = forge.resize((51, 51), Image.Resampling.LANCZOS)
    sword = Image.open(ASSETS_DIR / "51.png").convert("RGBA")
    sword = sword.resize((51, 51), Image.Resampling.LANCZOS)

    x = 0
    y = 0
    for badge in badges:
        if badge in BADGE_TO_IMAGE:
            if x == 4:
                y += 1
                x = 0
            badge_img = Image.open(BADGE_TO_IMAGE[badge]).convert("RGBA")
            badge_img = badge_img.resize((51, 51), Image.Resampling.LANCZOS)
            bg.paste(badge_img, (44 + 65 * x, 336 + 66 * y), badge_img)
            x += 1
    # bg.paste(forge, (29, 224), forge)
    # bg.paste(sword, (73, 224), sword)

    bg.paste(trophy, (525, 423), trophy)
    bg.paste(calendar, (525, 468), calendar)
    bg.paste(ticket, (363, 423), ticket)
    bg.paste(medal, (363, 470), medal)
    bg.paste(messages, (525, 252), messages)
    bg.paste(dice, (525, 297), dice)

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer, badges, is_potw, has_been_potw, target.display_name, wins
