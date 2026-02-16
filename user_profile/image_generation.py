import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, cast

from discord import Member
from PIL import Image, ImageDraw, ImageFont

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
) -> tuple[BytesIO, list[str]]:
    user_id = target.id
    server_id = interaction.guild.id
    mee6 = await fetch_mee6_stats(user_id, server_id)
    bg = Image.open(ASSETS_DIR / "card.png").convert("RGBA")
    draw = ImageDraw.Draw(bg)
    doc_ref = db.collection("users").document(str(user_id))

    doc = cast(Any, doc_ref.get())
    data: Dict[str, Any] = doc.to_dict() or {}

    badges = sort_badges(data.get("badges", []))
    points = data.get("points", 0)
    tickets_claimed = data.get("tickets_claimed", 0)
    guild = str(data.get("guild", "No guild"))
    users_above = db.collection("users").where("points", ">", points).stream()

    rank = sum(1 for _ in users_above) + 1

    avatar = await fetch_avatar(target.display_avatar.url)
    avatar = circle_crop(avatar, 154)

    # Paste position (x, y)
    bg.paste(avatar, (29, 21), avatar)

    font_big = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 36)
    font_bold = ImageFont.truetype(FONTS_DIR / "Urbanist-Bold.ttf", 44)
    font_light = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 16)
    font_small = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 20)
    font_xsmall = ImageFont.truetype(FONTS_DIR / "Urbanist-Regular.ttf", 16)
    font_xsmall_light = ImageFont.truetype(FONTS_DIR / "Urbanist-Light.ttf", 14)

    draw.text((227, 21), target.display_name, font=font_big, fill="#FFFFFF")

    draw.text((227, 61), guild, font=font_small, fill="#A0A0AA")

    if target.joined_at:
        day = target.joined_at.day
        joined_text = f"Joined {day}. {target.joined_at.strftime('%b %Y')}"
    else:
        joined_text = "Joined unknown"

    draw.text(
        (227, 96),
        joined_text,
        font=font_light,
        fill="#A0A0AA",
    )

    draw.text((29, 190), "Badges", font=font_small, fill="#FFFFFF")

    draw.text((237, 133), "Stats", font=font_small, fill="#FFFFFF")

    draw.text((255, 155), str(mee6["level"]), font=font_bold, fill="#FFFFFF")

    draw.text((240, 182), "lvl", font=font_xsmall, fill="#FFFFFF")

    draw.text(
        (240, 200),
        f"{mee6['current_xp']} / {mee6['xp_to_level']} xp",
        font=font_xsmall_light,
        fill="#A0A0AA",
    )

    draw.text((375, 167), f"{mee6['messages']} sent", font=font_xsmall, fill="#FFFFFF")

    draw.text((375, 197), "", font=font_xsmall, fill="#FFFFFF")

    draw.text((237, 250), "Tickets", font=font_small, fill="#FFFFFF")

    draw.text((267, 280), f"{tickets_claimed} helped", font=font_xsmall, fill="#FFFFFF")

    draw.text((267, 311), f"{points} points", font=font_xsmall, fill="#FFFFFF")

    draw.text((375, 280), "0 wins", font=font_xsmall, fill="#FFFFFF")

    draw.text(
        (375, 311),
        f"{ordinal(rank)} place",
        font=font_xsmall,
        fill="#FFFFFF",
    )

    trophy = Image.open(ASSETS_DIR / "trophy.png").convert("RGBA")
    trophy = trophy.resize((18, 18), Image.Resampling.LANCZOS)
    calendar = Image.open(ASSETS_DIR / "calendar.png").convert("RGBA")
    calendar = calendar.resize((18, 18), Image.Resampling.LANCZOS)
    ticket = Image.open(ASSETS_DIR / "ticket.png").convert("RGBA")
    ticket = ticket.resize((18, 18), Image.Resampling.LANCZOS)
    medal = Image.open(ASSETS_DIR / "medal.png").convert("RGBA")
    medal = medal.resize((18, 18), Image.Resampling.LANCZOS)
    dice = Image.open(ASSETS_DIR / "dice.png").convert("RGBA")
    dice = dice.resize((18, 18), Image.Resampling.LANCZOS)
    messages = Image.open(ASSETS_DIR / "messages.png").convert("RGBA")
    messages = messages.resize((18, 18), Image.Resampling.LANCZOS)
    forge = Image.open(ASSETS_DIR / "forge.png").convert("RGBA")
    forge = forge.resize((34, 34), Image.Resampling.LANCZOS)
    sword = Image.open(ASSETS_DIR / "51.png").convert("RGBA")
    sword = sword.resize((34, 34), Image.Resampling.LANCZOS)

    x = 0
    y = 0
    for badge in badges:
        if badge in BADGE_TO_IMAGE:
            if x == 4:
                y += 1
                x = 0
            badge_img = Image.open(BADGE_TO_IMAGE[badge]).convert("RGBA")
            badge_img = badge_img.resize((34, 34), Image.Resampling.LANCZOS)
            bg.paste(badge_img, (29 + 44 * x, 224 + 44 * y), badge_img)
            x += 1
    # bg.paste(forge, (29, 224), forge)
    # bg.paste(sword, (73, 224), sword)

    bg.paste(trophy, (350, 282), trophy)
    bg.paste(calendar, (350, 312), calendar)
    bg.paste(ticket, (242, 282), ticket)
    bg.paste(medal, (242, 313), medal)
    bg.paste(messages, (350, 168), messages)
    bg.paste(dice, (350, 198), dice)

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer, badges
