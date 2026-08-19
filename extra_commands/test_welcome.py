from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageSequence

from assets_caching import ASSET_CACHE, FONTS
from extra_commands.render import render_png

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"
FONTS_DIR = Path(__file__).parent.parent.parent / "assets" / "fonts"


async def text_welcome(username: str):
    image_buffer = await render_png(username)

    # Convert BytesIO -> PIL Image
    image = Image.open(image_buffer).convert("RGBA")

    im = Image.open(ASSETS_DIR / "welcome-gif")
    font_big = FONTS["claim_font"]

    frames = []

    for frame in ImageSequence.Iterator(im):
        frame = frame.copy().convert("RGBA")
        d = ImageDraw.Draw(frame)

        # -------------------------
        # Center the username
        # -------------------------
        text_bbox = d.textbbox(
            (0, 0),
            username,
            font=font_big,
        )

        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = (frame.width - text_width) // 2
        text_y = (frame.height - text_height) // 2

        d.text(
            (text_x, text_y),
            username,
            font=font_big,
            fill="#FFFFFF",
        )

        # -------------------------
        # Center the rendered image
        # -------------------------
        image_x = (frame.width - image.width) // 2
        image_y = (frame.height - image.height) // 2

        frame.paste(
            image,
            (image_x, image_y),
            image,
        )

        frames.append(frame)

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
