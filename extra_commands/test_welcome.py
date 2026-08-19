from io import BytesIO

from PIL import Image, ImageDraw, ImageSequence

from assets_caching import FONTS
from extra_commands.render import render_png
from user_profile.hand_border_test import ASSETS_DIR


IMAGE_SCALE = 1.2
IMAGE_BOTTOM_OFFSET = 180


async def text_welcome(username: str):
    image_buffer = await render_png(username)

    # BytesIO -> PIL Image
    image = Image.open(image_buffer).convert("RGBA")

    im = Image.open(ASSETS_DIR / "welcome-gif.gif")
    font_big = FONTS["bold"]

    frames = []

    for frame in ImageSequence.Iterator(im):
        frame = frame.copy().convert("RGBA")
        d = ImageDraw.Draw(frame)

        # -------------------------
        # Username
        # -------------------------
        text_bbox = d.textbbox(
            (0, 0),
            f"Welcome {username}",
            font=font_big,
        )

        text_width = text_bbox[2] - text_bbox[0]

        text_x = (frame.width - text_width) // 2
        text_y = (frame.height - 40)

        d.text(
            (text_x, text_y),
            f"Welcome {username}",
            font=font_big,
            fill="#FFFFFF",
        )

        # -------------------------
        # Scale rendered image
        # -------------------------
        new_width = int(image.width * IMAGE_SCALE)
        new_height = int(image.height * IMAGE_SCALE)

        scaled_image = image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS,
        )

        # -------------------------
        # Center image horizontally
        # -------------------------
        image_x = (frame.width - scaled_image.width) // 2

        # Position image so it extends below
        # the bottom of the GIF.
        image_y = (
            frame.height
            - scaled_image.height
            + IMAGE_BOTTOM_OFFSET
        )

        # Anything outside the GIF boundaries
        # is automatically cropped.
        frame.paste(
            scaled_image,
            (image_x, image_y),
            scaled_image,
        )
        d.text(
            (text_x, text_y),
            f"Welcome {username}",
            font=font_big,
            fill="#FFFFFF",
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
