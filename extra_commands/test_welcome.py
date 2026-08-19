from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageSequence

from assets_caching import ASSET_CACHE, FONTS
from extra_commands.render import render_png

ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"


async def text_welcome(username: str):
    image_buffer = await render_png(username)

    # BytesIO -> PIL Image
    image = Image.open(image_buffer).convert("RGBA")

    im = Image.open(ASSET_CACHE["welcome-gif"])
    font_big = FONTS["claim_font"]

    frames = []

    for frame in ImageSequence.Iterator(im):
        frame = frame.copy().convert("RGBA")
        d = ImageDraw.Draw(frame)

        # -------------------------
        # Username
        # -------------------------
        text_bbox = d.textbbox(
            (0, 0),
            username,
            font=font_big,
        )

        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Space between username and image
        spacing = 10

        # -------------------------
        # Scale image to fit GIF
        # -------------------------
        padding = 10

        max_image_height = (
            frame.height
            - text_height
            - spacing
            - padding * 2
        )

        if image.height > max_image_height:
            scale = max_image_height / image.height

            new_width = int(image.width * scale)
            new_height = int(image.height * scale)

            scaled_image = image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS,
            )
        else:
            scaled_image = image

        # -------------------------
        # Center entire composition
        # -------------------------
        total_height = (
            text_height
            + spacing
            + scaled_image.height
        )

        start_y = (frame.height - total_height) // 2

        # Username
        text_x = (frame.width - text_width) // 2

        d.text(
            (text_x, start_y),
            username,
            font=font_big,
            fill="#FFFFFF",
        )

        # Rendered image
        image_x = (frame.width - scaled_image.width) // 2
        image_y = start_y + text_height + spacing

        frame.paste(
            scaled_image,
            (image_x, image_y),
            scaled_image,
        )

        frames.append(frame)

    buffer = BytesIO()

    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=im.info.get("duration", 100),
        disposal=2,
    )

    buffer.seek(0)

    return buffer
