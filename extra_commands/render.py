import asyncio
import base64
import html
import re
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

from aiohttp import web
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from request_utils import rate_limited_get_text

WIDTH = 715
HEIGHT = 455

_server_started = False

BASE_DIR = Path(__file__).resolve().parent

SWF_PATH = BASE_DIR.parent / "assets/testing2.swf"

HTML_PATH = BASE_DIR.parent / "extra_commands/render.html"


async def start_server():

    global _server_started

    if _server_started:
        return

    app = web.Application()

    async def render_html(request):

        return web.FileResponse(HTML_PATH)

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


def get_driver():

    options = Options()

    options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")

    options.add_argument("--disable-dev-shm-usage")

    options.add_argument("--window-size=715,455")

    options.add_argument("--disable-gpu")

    options.add_argument("--force-device-scale-factor=1")

    options.add_argument("--hide-scrollbars")

    options.page_load_strategy = "eager"

    driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(20)

    return driver


async def get_flashvars(username: str):

    source = await rate_limited_get_text(
        f"https://account.aq.com/CharPage?id={username}"
    )

    match = re.search(r'flashvars="([^"]+)"', source, re.IGNORECASE)

    if not match:
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(source)

        raise Exception("FlashVars not found")

    flashvars = html.unescape(match.group(1))

    return flashvars


def crop_image(image):

    bbox = image.getbbox()

    if bbox:
        image = image.crop(bbox)

    return image


async def get_canvas(driver):

    for _ in range(200):
        try:
            ruffle = await run_blocking(
                driver.find_element, By.CSS_SELECTOR, "ruffle-embed, ruffle-object"
            )

            canvas = await run_blocking(
                lambda: ruffle.shadow_root.find_element(By.CSS_SELECTOR, "canvas")
            )

            return canvas

        except Exception:
            await asyncio.sleep(0.1)

    raise Exception("Canvas not found")


async def setup_page(username: str):

    await start_server()

    flash_vars = await get_flashvars(username)

    driver = get_driver()

    encoded = quote(flash_vars)

    url = f"http://127.0.0.1:8765/render.html?flashVars={encoded}"

    await run_blocking(driver.get, url)

    # AQW assets load slowly
    await asyncio.sleep(5)

    return driver


async def run_blocking(func, *args):
    return await asyncio.to_thread(func, *args)


async def render_png(username: str):

    driver = await setup_page(username)

    canvas = await get_canvas(driver)

    # get the canvas as a PNG base64 string
    canvas_base64 = driver.execute_script(
        "return arguments[0].toDataURL('image/png').substring(21);", canvas
    )

    # decode
    png = base64.b64decode(canvas_base64)

    image = Image.open(BytesIO(png)).convert("RGBA")

    image = crop_image(image)

    output = BytesIO()

    image.save(output, format="PNG")

    output.seek(0)
    driver.quit()
    return output


async def render_gif(username: str):

    driver = await setup_page(username)

    frames = []

    await asyncio.sleep(1)

    for _ in range(40):
        canvas = await get_canvas(driver)

        canvas_base64 = driver.execute_script(
            "return arguments[0].toDataURL('image/png').substring(21);", canvas
        )

        png = base64.b64decode(canvas_base64)

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
    driver.quit()
    return output
