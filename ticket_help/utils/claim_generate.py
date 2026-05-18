import asyncio
from io import BytesIO
from pathlib import Path

import discord
from PIL import Image, ImageDraw, ImageFont

from assets_caching import ASSET_CACHE, FONTS
from user_profile.utils import circle_crop, fetch_avatar

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
FONTS_DIR = Path(__file__).parent.parent.parent / "assets" / "fonts"
BG = ASSET_CACHE["claim"]


async def generate_claim(
    username: str,
    claimed: bool,
    status: str,
    user: discord.User,
):
    bg = BG.copy()
    font_big = FONTS["claim_font"]
    claim_text = "claimed" if claimed else "unclaimed"
    avatar_url = user.display_avatar.replace(format="png", size=128).url
    avatar = await fetch_avatar(avatar_url)

    avatar = circle_crop(avatar, 100)
    bg.paste(avatar, (10, 10), avatar)
    draw = ImageDraw.Draw(bg)
    draw.text(
        (130, 34),
        f"{username} {claim_text} - {status}",
        font=font_big,
        fill="#12DD4F" if claimed else "#FF0400",
    )
    avatar = circle_crop(avatar, 100)
    buffer = BytesIO()

    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer
