import asyncio
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, cast

from discord import Member
from PIL import Image, ImageDraw, ImageFont

from config import POTW_ROLE_ID
from firebase_client import db
from user_profile.image_utils import draw_gradient_text

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
    total_guesses = game_data.get("total_guesses", 0)
    games_played = game_data.get("games_played", 0)
    if games_played > 0:
        avg_guesses = round(total_guesses / games_played, 2)
    else:
        avg_guesses = 0
    avg_display = f"{avg_guesses}" if games_played > 0 else "—"
    completed_words = game_data.get("words_completed", 0)
    users_above = list(db.collection("users").where("points", ">", points).stream())
    counting_score = data.get("counting_score", 0)
    rank = len(users_above) + 1
    coins = data.get("coins", 0)
    wins = data.get("wins", 0)
    border = data.get("border", {})
    card = data.get("card", {})
    gems = data.get("gems", 0)
    bg = Image.open(ASSETS_DIR / f"test_card2.png").convert("RGBA")
    role = data.get("highlighted_role", "None")

    # if border:
    #    border_img = Image.open(ASSETS_DIR / f"{border.get('image')}").convert("RGBA")
    #    bg.paste(border_img, (0, 0), border_img)

    draw = ImageDraw.Draw(bg)
    avatar = Image.open(ASSETS_DIR / "custom.png").convert("RGBA")
    avatar = circle_crop(avatar, 218)
    bg.paste(avatar, (43, 37), avatar)

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
    font_xsmall_bold = load_font("Urbanist-Bold.ttf", 24)
    font_small_bold = load_font("Urbanist-Bold.ttf", 27)
    font_xsmall_light = load_font("Urbanist-Light.ttf", 21)
    role = "Grand Oathsworn"
    draw.text((302, 32), "Proxy", font=font_big, fill="#FFFFFF")
    if has_been_potw:
        name = "Proxy"
        name_x = 302
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
    draw.text((302, 92), guild, font=font_small, fill="#FFFFFF")

    joined_text = "Joined unknown"

    draw.text(
        (302, 144),
        joined_text,
        font=font_xsmall,
        fill="#FFFFFF",
    )

    draw.text((335, 175), str(100), font=font_bold, fill="#FFFFFF")

    draw.text((312, 215), "lvl", font=font_xsmall, fill="#FFFFFF")

    draw.text(
        (312, 242),
        f"1234 / 2345 xp",
        font=font_xsmall_light,
        fill="#FFFFFF",
    )
    draw_gradient_text(bg, (467, 196), "@", font_small_bold, role)
    draw_gradient_text(
        bg,
        (500, 197),
        role,
        font_xsmall_bold,
    )
    draw.text((500, 232), f"1112 messages", font=font_xsmall, fill="#FFFFFF")

    draw.text((346, 387), f"{counting_score} counts", font=font_xsmall, fill="#FFFFFF")

    draw.text((535, 305), f"{gems}", font=font_xsmall, fill="#FFFFFF")

    draw.text((346, 428), f"{points} points", font=font_xsmall, fill="#FFFFFF")
    draw.text((346, 346), f"{completed_words} words", font=font_xsmall, fill="#FFFFFF")

    draw.text((346, 305), f"{coins}", font=font_xsmall, fill="#FFFFFF")
    draw.text((535, 346), f"{avg_display}", font=font_xsmall, fill="#FFFFFF")
    draw.text((346, 469), f"{wins} wins", font=font_xsmall, fill="#FFFFFF")
    draw.text(
        (535, 428), f"{tickets_claimed} tickets", font=font_xsmall, fill="#FFFFFF"
    )

    draw.text(
        (535, 469),
        f"{ordinal(rank)} place",
        font=font_xsmall,
        fill="#FFFFFF",
    )

    coin = load_asset("coin.png", (26, 27))
    trophy = load_asset("trophy.png", (24, 24))
    podium = load_asset("podium.png", (30, 30))
    gem = load_asset("gem.png", (27, 27))
    medal = load_asset("medal.png", (27, 27))
    dice = load_asset("dice.png", (24, 24))
    messages = load_asset("messages.png", (25, 25))
    aqwordle = load_asset("aqwordle.webp", (26, 26))
    average = load_asset("average.png", (27, 27))
    ticket = load_asset("ticket.png", (25, 25))

    x = 0
    y = 0
    for badge in badges:
        if badge in BADGE_TO_IMAGE:
            badge_img = Image.open(BADGE_TO_IMAGE[badge]).convert("RGBA")
            badge_img = badge_img.resize((69, 69), Image.Resampling.LANCZOS)
            if x == 3:
                y += 1
                x = 0
            bg.paste(badge_img, (36 + 81 * x, 291 + 81 * y), badge_img)
            x += 1
    # bg.paste(forge, (29, 224), forge)
    # bg.paste(sword, (73, 224), sword)

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
    bg.save("test_image.png", format="PNG")
    buffer.seek(0)

    return buffer, badges, False, has_been_potw, "Proxy", wins
