import asyncio
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

import aiohttp
from aiohttp import web
from PIL import Image
from playwright.async_api import async_playwright

WIDTH = 715
HEIGHT = 455

_browser = None
_playwright = None
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


async def get_browser():

    global _browser
    global _playwright

    if _browser is None:
        _playwright = await async_playwright().start()

        _browser = await _playwright.chromium.launch(headless=True)

    return _browser


async def get_flashvars(username: str):

    browser = await get_browser()

    page = await browser.new_page()

    await page.goto(f"https://account.aq.com/CharPage?id={username}")

    # AQW loads slowly
    await page.wait_for_timeout(5000)

    flashvars = await page.evaluate("""
    () => {

        const param =
            document.querySelector(
                'param[name="FlashVars"]'
            );

        if (!param) {
            return null;
        }

        return param.getAttribute(
            "value"
        );
    }
    """)

    await page.close()

    if not flashvars:
        raise Exception("FlashVars not found")

    return flashvars


async def get_canvas(page):

    for _ in range(200):
        ruffle = await page.query_selector("ruffle-embed, ruffle-object")

        if ruffle:
            handle = await ruffle.evaluate_handle(
                """
                    (el) => {

                        return (
                            el.shadowRoot
                                ?.querySelector(
                                    "canvas"
                                )
                        );
                    }
                    """
            )

            canvas = handle.as_element()

            if canvas:
                return canvas

        await asyncio.sleep(0.1)

    raise Exception("Canvas not found")


def crop_image(image):

    bbox = image.getbbox()

    if bbox:
        image = image.crop(bbox)

    return image


async def setup_page(username: str):

    await start_server()

    flash_vars = await get_flashvars(username)

    browser = await get_browser()

    page = await browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})

    encoded = quote(flash_vars)

    url = f"http://127.0.0.1:8765/render.html?flashVars={encoded}"

    await page.goto(url)

    # AQW assets can take awhile
    await page.wait_for_timeout(200)

    canvas = await get_canvas(page)

    return page, canvas


async def render_png(username: str):

    page, canvas = await setup_page(username)

    png = await canvas.screenshot(type="png", omit_background=True)

    await page.close()

    image = Image.open(BytesIO(png)).convert("RGBA")

    image = crop_image(image)

    output = BytesIO()

    image.save(output, format="PNG")

    output.seek(0)

    return output


async def render_gif(username: str):

    page, canvas = await setup_page(username)

    frames = []
    await asyncio.sleep(0.2)

    for _ in range(40):
        png = await canvas.screenshot(type="png", omit_background=True)

        frame = Image.open(BytesIO(png)).convert("RGBA")

        frames.append(frame)

        await asyncio.sleep(0.05)

    await page.close()

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
