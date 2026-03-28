# 2. Create gradient (FAST VERSION)
from PIL import Image, ImageDraw

ROLES_COLOR_MAP = {
    "Initiate": ["ffffff", "80daeb"],
    "Unsworn": ["ffffff", "ffffff"],
    "Guide Writer": ["9e6bff", "9fc1ff"],
    "AE Staff": ["b19550", "f6fda6"],
    "Oathkeeper": ["f17a7a", "f0bbbb"],
    "Grand Oathsworn": ["aa3b3b", "ff4848"],
    "Oathsworn": ["ec3939", "cfab29"],
    # "POTW": ["369876", "71ff9e"],
    "Vow Council": ["ffffff", "ec9fff"],
    "Ascended": ["9b8666", "ffe1b4"],
    "Founder": ["f5e20c", "f1ff9f"],
    "Oath Pillar": ["d4843d", "ffde90"],
    "Arbiter": ["b2eb80", "80daeb"],
    "Oathist": ["80ebc2", "80ebc2"],
    "Cornerstone": ["b2eb80", "b2eb80"],
    "Beta Tester": ["", ""],
    "Ticket Inspector": ["9d5100", "febe58"],
    "Ticket Officer": ["f684da", "80daeb"],
}


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")

    if len(hex_color) != 6:
        raise ValueError("Hex color must be 6 characters")

    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16),
    )


def draw_gradient_text(
    base_image: Image.Image,
    position: tuple[int, int],
    text: str,
    font,
    force_color: str | None = None,
):
    if force_color:
        color = ROLES_COLOR_MAP.get(force_color, ["ffffff", "ffffff"])
        start_color = hex_to_rgb(color[0])
        end_color = hex_to_rgb(color[1])
    else:
        color = ROLES_COLOR_MAP.get(text, ["ffffff", "ffffff"])
        start_color = hex_to_rgb(color[0])
        end_color = hex_to_rgb(color[1])

    x, y = position

    draw = ImageDraw.Draw(base_image)

    # 1. Get bbox (IMPORTANT)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 2. Create gradient
    gradient = Image.new("RGB", (1, text_height))

    for y_pos in range(text_height):
        ratio = y_pos / text_height
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)

        gradient.putpixel((0, y_pos), (r, g, b))

    gradient = gradient.resize((text_width, text_height))

    # 3. Create mask
    mask = Image.new("L", (text_width, text_height), 0)
    mask_draw = ImageDraw.Draw(mask)

    mask_draw.text((-bbox[0], -bbox[1]), text, font=font, fill=255)

    # 4. Paste
    base_image.paste(gradient, (x, y), mask)
