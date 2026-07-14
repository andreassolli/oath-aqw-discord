import asyncio
from io import BytesIO
from pathlib import Path

import discord
from PIL import Image, ImageDraw, ImageFont

from assets_caching import ASSET_CACHE, FONTS
from user_profile.utils import circle_crop, fetch_avatar

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
FONTS_DIR = Path(__file__).parent.parent.parent / "assets" / "fonts"


async def generate_claim(
    username: str,
    claimed: bool,
    status: str,
    user: discord.User,
    image: str | None = None,
    role_change: bool = False,
    selected_role: str = "",
):
    if image is not None:
        bg = Image.open(ASSETS_DIR / image)
    else:
        bg = ASSET_CACHE["claim"]

    icon = ASSET_CACHE["plus"] if claimed else ASSET_CACHE["minus"]
    bg = bg.copy()
    font_big = FONTS["claim_font"]
    claim_text = "claimed" if claimed else f"unclaimed {status}"
    role_text = f"{selected_role}"
    full_claim_text = claim_text
    if not role_change:
        if selected_role == "ArchPaladin":
            selected_role = "AP"
        elif selected_role == "Lord of Order":
            selected_role = "LOO"
        elif selected_role == "Legion Revenant":
            selected_role = "LR"
    if claimed:
        full_claim_text = (
            f"swapped to {role_text}"
            if role_change
            else f"{claim_text} {role_text} {status}"
        )

    avatar_url = user.display_avatar.replace(format="png", size=128).url
    avatar = await fetch_avatar(avatar_url)

    avatar = circle_crop(avatar, 100)

    bg.paste(avatar, (10, 10), avatar)
    if not role_change:
        bg.paste(icon, (bg.width - 110, 10), icon)
    draw = ImageDraw.Draw(bg)
    draw.text(
        (130, 34),
        f"{username} {full_claim_text}",
        font=font_big,
        fill="#FFFFFF",
    )
    avatar = circle_crop(avatar, 100)
    buffer = BytesIO()

    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
