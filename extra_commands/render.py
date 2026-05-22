import asyncio
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

from aiohttp import web
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

WIDTH = 715
HEIGHT = 455

_server_started = False

BASE_DIR = Path(__file__).resolve().parent

SWF_PATH = BASE_DIR.parent / "assets" / "testing2.swf"


async def start_server():

    global _server_started

    if _server_started:
        return

    app = web.Application()

    async def render_html(request):

        return web.FileResponse("render.html")

    async def testing2(request):

        return web.FileResponse(SWF_PATH)

    app.router.add_get("/render.html", render_html)

    app.router.add_get("/testing2.swf", testing2)

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(runner, "127.0.0.1", 8765)

    await site.start()

    _server_started = True

    print("Render server started")


_driver = None


def get_driver():

    global _driver

    if _driver is None:
        options = Options()

        options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")

        options.add_argument("--disable-dev-shm-usage")

        options.add_argument("--window-size=715,455")

        options.add_argument("--disable-gpu")

        _driver = webdriver.Chrome(options=options)

    return _driver


async def get_flashvars(username: str):

    driver = get_driver()

    driver.get(f"https://account.aq.com/CharPage?id={username}")

    await asyncio.sleep(5)

    param = driver.find_element(By.CSS_SELECTOR, 'param[name="FlashVars"]')

    flashvars = param.get_attribute("value")

    if not flashvars:
        raise Exception("FlashVars not found")

    return flashvars


def crop_image(image):

    bbox = image.getbbox()

    if bbox:
        image = image.crop(bbox)

    return image


async def setup_page(username: str):

    await start_server()

    flash_vars = await get_flashvars(username)

    driver = get_driver()

    encoded = quote(flash_vars)

    url = f"http://127.0.0.1:8765/render.html?flashVars={encoded}"

    driver.get(url)

    # AQW assets load slowly
    await asyncio.sleep(5)

    return driver


async def render_png(username: str):

    driver = await setup_page(username)

    png = driver.get_screenshot_as_png()

    image = Image.open(BytesIO(png)).convert("RGBA")

    image = crop_image(image)

    output = BytesIO()

    image.save(output, format="PNG")

    output.seek(0)

    return output


async def render_gif(username: str):

    driver = await setup_page(username)

    frames = []

    await asyncio.sleep(1)

    for _ in range(40):
        png = driver.get_screenshot_as_png()

        frame = Image.open(BytesIO(png)).convert("RGBA")

        frame = crop_image(frame)

        frames.append(frame.copy())

        await asyncio.sleep(0.05)

    output = BytesIO()

    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=40,
        loop=0,
        disposal=2,
    )

    output.seek(0)

    return output
