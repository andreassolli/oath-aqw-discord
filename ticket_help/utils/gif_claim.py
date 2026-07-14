import asyncio
from io import BytesIO
from pathlib import Path

import discord
from PIL import Image, ImageDraw, ImageFont, ImageSequence

from assets_caching import ASSET_CACHE, FONTS
from user_profile.utils import circle_crop, fetch_avatar

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
FONTS_DIR = Path(__file__).parent.parent.parent / "assets" / "fonts"


async def gif_claim(
    username: str,
    claimed: bool,
    status: str,
    user: discord.User,
    gif: str = "akame-claim.gif",
    role_change: bool = False,
    selected_role: str = "",
):

    im = Image.open(ASSETS_DIR / gif)
    font_big = FONTS["claim_font"]
    if not role_change:
        if selected_role == "ArchPaladin":
            selected_role = "AP"
        elif selected_role == "Lord of Order":
            selected_role = "LOO"
        elif selected_role == "Legion Revenant":
            selected_role = "LR"
    claim_text = "claimed" if claimed else f"unclaimed {status}"
    role_text = f"{selected_role}"
    full_claim_text = claim_text
    if claimed:
        full_claim_text = (
            f"swapped to {role_text}"
            if role_change
            else f"{claim_text} {role_text} {status}"
        )
    
    avatar_url = user.display_avatar.replace(format="png", size=128).url
    avatar = await fetch_avatar(avatar_url)
    avatar = circle_crop(avatar, 100)
    icon = ASSET_CACHE["plus"] if claimed else ASSET_CACHE["minus"]

    # A list of the frames to be outputted
    frames = []
    for frame in ImageSequence.Iterator(im):
        frame = frame.copy().convert("RGBA")

        d = ImageDraw.Draw(frame)

        d.text(
            (130, 34),
            f"{username} {full_claim_text}",
            font=font_big,
            fill="#FFFFFF",
        )

        frame.paste(avatar, (10, 10), avatar)
        if not role_change:
            frame.paste(icon, (frame.width - 110, 10), icon)

        frames.append(frame)
    # Save the frames as a new image
    buffer = BytesIO()

    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        loop=0,
    )

    buffer.seek(0)

    return buffer
