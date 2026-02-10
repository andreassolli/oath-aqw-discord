from io import BytesIO

import aiohttp
from PIL import Image, ImageDraw


async def fetch_avatar(url: str) -> Image.Image:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.read()
    return Image.open(BytesIO(data)).convert("RGBA")


def circle_crop(img, size):
    img = img.resize((size, size))
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, size, size), fill=255)
    img.putalpha(mask)
    return img
