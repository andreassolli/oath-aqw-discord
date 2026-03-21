import asyncio
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, cast

from discord import Member
from PIL import Image, ImageDraw, ImageFont

from assets_caching import ASSET_CACHE, BADGE_CACHE, FONTS
from config import POTW_ROLE_ID
from firebase_client import db

from .mee6_fetcher import fetch_mee6_stats
from .utils import circle_crop, fetch_avatar, ordinal, sort_badges

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


async def generate_profile_card(
    interaction,
    target: Member,
) -> tuple[BytesIO, list[str], bool, bool, str, int]:
    user_id = target.id
    server_id = interaction.guild.id

    mee6_task = fetch_mee6_stats(user_id, server_id)
    avatar_task = fetch_avatar(target.display_avatar.url)

    mee6, avatar = await asyncio.gather(mee6_task, avatar_task)

    doc_ref = db.collection("users").document(str(user_id))

    doc = cast(Any, doc_ref.get())
    data: Dict[str, Any] = doc.to_dict() or {}

    badges = sort_badges(data.get("badges", []))
    points = data.get("points", 0)
    tickets_claimed = data.get("tickets_claimed", 0)
    guild = str(data.get("guild", "No guild"))
    if guild == "None":
        guild = "No guild"
    has_been_potw = data.get("has_been_potw", False)
    is_potw = any(role.id == POTW_ROLE_ID for role in target.roles)
    game_ref = db.collection("wordle_games").document(str(target.id))
    game_doc = game_ref.get()
    game_data = game_doc.to_dict() if game_doc.exists else {}
    completed_words = game_data.get("words_completed", 0)
    users_above = list(db.collection("users").where("points", ">", points).stream())
    rank = len(users_above) + 1
    coins = data.get("coins", 0)
    wins = data.get("wins", 0)
    border = data.get("border", "")
    card = data.get("card", {})
    if card:
        bg = Image.open(ASSETS_DIR / f"{card.get('image')}").convert("RGBA")
    else:
        bg = ASSET_CACHE["default_bg"].copy()
    draw = ImageDraw.Draw(bg)
    avatar = circle_crop(avatar, 231)
    bg.paste(avatar, (44, 32), avatar)

    # if border == "Test Border":
    #    test_border = Image.open(ASSETS_DIR / "test_border.png").convert("RGBA")
    #    bg.paste(test_border, (0, 0), test_border)
    if is_potw:
        potw_border = ASSET_CACHE["potw_border"]
        bg.paste(potw_border, (27, 19), potw_border)

    font_big = FONTS["big"]
    font_bold = FONTS["bold"]
    font_light = FONTS["light"]
    font_small = FONTS["small"]
    font_xsmall = FONTS["xsmall"]
    font_xsmall_light = FONTS["xsmall_light"]

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

        potw_flare = ASSET_CACHE["potw_flare"]
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

    draw.text((563, 420), f"{coins}", font=font_xsmall, fill="#FFFFFF")

    draw.text(
        (563, 467),
        f"{ordinal(rank)} place",
        font=font_xsmall,
        fill="#FFFFFF",
    )

    trophy = ASSET_CACHE["trophy"]
    calendar = ASSET_CACHE["calendar"]
    ticket = ASSET_CACHE["ticket"]
    medal = ASSET_CACHE["medal"]
    dice = ASSET_CACHE["dice"]
    messages = ASSET_CACHE["messages"]

    x = 0
    y = 0
    for badge in badges:
        if badge in BADGE_CACHE:
            if x == 4:
                y += 1
                x = 0
            badge_img = BADGE_CACHE[badge]
            bg.paste(badge_img, (44 + 65 * x, 337 + 66 * y), badge_img)
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
