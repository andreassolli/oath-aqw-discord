import asyncio
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, cast

from discord import Member
from PIL import Image, ImageDraw, ImageFont

from assets_caching import ASSET_CACHE, BADGE_CACHE, FONTS
from config import AQW_BADGES, POTW_ROLE_ID
from firebase_client import db
from user_profile.image_utils import draw_gradient_text

from .mee6_fetcher import fetch_mee6_stats
from .utils import circle_crop, fetch_avatar, ordinal, sort_badges

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


async def generate_profile_card(
    interaction,
    target: Member,
    gold_card: bool = False,
) -> tuple[BytesIO, list[str], bool, bool, str, int]:
    user_id = target.id
    server_id = interaction.guild.id

    mee6_task = fetch_mee6_stats(user_id, server_id)
    avatar_url = target.display_avatar.replace(format="png", size=256).url
    avatar_task = fetch_avatar(avatar_url)

    mee6, avatar = await asyncio.gather(mee6_task, avatar_task)

    doc_ref = db.collection("users").document(str(user_id))

    doc = cast(Any, doc_ref.get())
    data: Dict[str, Any] = doc.to_dict() or {}

    badges = sort_badges(data.get("badges", []))
    points = data.get("points", 0)
    tickets_claimed = data.get("tickets_claimed", 0)
    guild = str(data.get("guild", ""))
    if guild == "None":
        guild = ""
    has_been_potw = data.get("has_been_potw", False)
    is_potw = any(role.id == POTW_ROLE_ID for role in target.roles)
    game_ref = db.collection("wordle_games").document(str(target.id))
    game_doc = game_ref.get()
    game_data = game_doc.to_dict() if game_doc.exists else {}
    total_guesses = game_data.get("total_guesses", 0)
    games_played = game_data.get("games_played", 0)
    if games_played > 0:
        avg_guesses = round(total_guesses / games_played, 2)
    else:
        avg_guesses = 0
    avg_display = f"{avg_guesses}" if games_played > 0 else "—"
    completed_words = game_data.get("words_completed", 0)
    users_above = list(db.collection("users").where("points", ">", points).stream())
    rank = len(users_above) + 1
    counting_score = data.get("counting_score", 0)
    coins = data.get("coins", 0)
    wins = data.get("wins", 0)
    border = data.get("border", {})
    card = data.get("card", {})
    gems = data.get("gems", 0)
    role = data.get("highlighted_role", "None")
    color = "#FFFFFF"
    outline_color = "#FFFFFF"
    outline_width = 0
    if target.joined_at:
        day = target.joined_at.day
        joined_text = f"Joined {day}. {target.joined_at.strftime('%b %Y')}"
    else:
        joined_text = "Joined unknown"

    if card:
        bg = Image.open(ASSETS_DIR / f"{card.get('image')}").convert("RGBA")
    else:
        bg = ASSET_CACHE["default_bg"].copy()

    if gold_card:
        bg = Image.open(ASSETS_DIR / "gold_signature_card.png").convert("RGBA")
        outline_color = "#583400"
        outline_width = 0

    if border and not gold_card:
        border_img = Image.open(ASSETS_DIR / f"{border.get('image')}").convert("RGBA")
        bg.paste(border_img, (0, 0), border_img)

    draw = ImageDraw.Draw(bg)
    avatar = circle_crop(avatar, 218)
    bg.paste(avatar, (43, 37), avatar)

    if is_potw:
        potw_border = ASSET_CACHE["potw_border"]
        bg.paste(potw_border, (39, 32), potw_border)

    font_big = FONTS["big"]
    font_bold = FONTS["bold"]
    font_light = FONTS["light"]
    font_small = FONTS["small"]
    font_xsmall = FONTS["xsmall"]
    font_xsmall_light = FONTS["xsmall_light"]
    font_small_bold = FONTS["small_bold"]
    font_xsmall_bold = FONTS["xsmall_bold"]
    if gold_card:
        draw.text(
            (304, 34),
            target.display_name,
            font=font_big,
            fill=outline_color,
            stroke_fill=outline_color,
            stroke_width=outline_width,
        )
        draw.text(
            (304, 146),
            joined_text,
            font=font_xsmall,
            fill=outline_color,
            stroke_fill=outline_color,
            stroke_width=outline_width,
        )
        draw.text(
            (304, 94),
            guild,
            font=font_small,
            fill=outline_color,
            stroke_fill=outline_color,
            stroke_width=outline_width,
        )
    draw.text(
        (302, 32),
        target.display_name,
        font=font_big,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )
    if has_been_potw:
        name = target.display_name
        name_x = 302
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
    draw.text(
        (302, 92),
        guild,
        font=font_small,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )

    draw.text(
        (302, 144),
        joined_text,
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )

    draw.text(
        (312, 242),
        f"{mee6['current_xp']} / {mee6['xp_to_level']} xp",
        font=font_xsmall_light,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )
    draw_gradient_text(bg, (467, 196), "@", font_small_bold, role)
    draw_gradient_text(
        bg,
        (500, 197),
        role,
        font_xsmall_bold,
    )
    draw.text(
        (335, 175),
        str(mee6["level"]),
        font=font_bold,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )

    draw.text(
        (312, 215),
        "lvl",
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )

    draw.text(
        (500, 232),
        f"{mee6['messages']} messages",
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )

    draw.text(
        (346, 387),
        f"{counting_score} counts",
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )

    draw.text(
        (535, 305),
        f"{gems}",
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )

    draw.text(
        (346, 428),
        f"{points} points",
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )
    draw.text(
        (346, 346),
        f"{completed_words} words",
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )

    draw.text(
        (346, 305),
        f"{coins}",
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )
    draw.text(
        (535, 346),
        f"{avg_display}",
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )
    draw.text(
        (346, 469),
        f"{wins} wins",
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )
    draw.text(
        (535, 428),
        f"{tickets_claimed} tickets",
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )

    draw.text(
        (535, 469),
        f"{ordinal(rank)} place",
        font=font_xsmall,
        fill=color,
        stroke_fill=outline_color,
        stroke_width=outline_width,
    )

    trophy = ASSET_CACHE["trophy"]
    coin = ASSET_CACHE["coin"]
    gem = ASSET_CACHE["gem"]
    medal = ASSET_CACHE["medal"]
    dice = ASSET_CACHE["dice"]
    messages = ASSET_CACHE["messages"]
    aqwordle = ASSET_CACHE["aqwordle"]
    ticket = ASSET_CACHE["ticket"]
    podium = ASSET_CACHE["podium"]
    average = ASSET_CACHE["average"]

    x = 0
    y = 0
    for badge in badges:
        if badge in BADGE_CACHE:
            if x == 3:
                y += 1
                x = 0
            badge_img = BADGE_CACHE[badge]
            bg.paste(badge_img, (36 + 81 * x, 291 + 81 * y), badge_img)
            x += 1

    bg.paste(coin, (312, 308), coin)
    bg.paste(podium, (495, 469), podium)
    bg.paste(gem, (497, 308), gem)
    bg.paste(medal, (311, 431), medal)
    bg.paste(ticket, (498, 430), ticket)
    bg.paste(messages, (468, 235), messages)
    bg.paste(dice, (313, 391), dice)
    bg.paste(aqwordle, (311, 349), aqwordle)
    bg.paste(average, (497, 349), average)
    bg.paste(trophy, (313, 474), trophy)

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer, badges, is_potw, has_been_potw, target.display_name, wins
