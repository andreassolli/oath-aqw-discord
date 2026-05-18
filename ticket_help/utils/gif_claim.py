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
):
    im = Image.open(ASSETS_DIR / "akame.gif")
    font_big = FONTS["claim_font"]
    claim_text = "claimed" if claimed else "unclaimed"
    avatar_url = user.display_avatar.replace(format="png", size=128).url
    avatar = await fetch_avatar(avatar_url)
    avatar = circle_crop(avatar, 51)

    # A list of the frames to be outputted
    frames = []
    # Loop over each frame in the animated image
    for frame in ImageSequence.Iterator(im):
        # Draw the text on the frame
        d = ImageDraw.Draw(frame)
        d.text(
            (66, 17),
            f"{username} {claim_text} - {status}",
            font=font_big,
            fill="#12DD4F" if claimed else "#FF0400",
        )

        del d

        # However, 'frame' is still the animated image with many frames
        # It has simply been seeked to a later frame
        # For our list of frames, we only want the current frame

        # Saving the image without 'save_all' will turn it into a single frame image, and we can then re-open it
        # To be efficient, we will save it to a stream, rather than to file
        b = BytesIO()
        frame.save(b, format="GIF")
        frame = Image.open(b)
        frame.paste(avatar, (5, 5), avatar)

        # Then append the single frame image to a list of frames
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
