import asyncio
import base64
import html
import re
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qsl, quote, urlencode

from aiohttp import web
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from config import PROXY_SERVICE
from http_client import get_session
from request_utils import HEADERS, rate_limited_get_text

WIDTH = 715
HEIGHT = 455
ASSET_CACHE = {}
_server_started = False

BASE_DIR = Path(__file__).resolve().parent

SWF_PATH = BASE_DIR.parent / "assets/testing2.swf"

HTML_PATH = BASE_DIR.parent / "extra_commands/render.html"

WEAPON_FIELDS = {
    "Sword",
    "Axe",
    "Dagger",
    "Polearm",
    "Bow",
    "Mace",
    "Staff",
    "Wand",
    "HandGun",
    "Rifle",
    "Whip",
    "Gun",
    "Gauntlet"
}
ITEM_FIELDS = {
    "Armor": {
        "file": "strCustArmorFile",
        "link": "strCustArmorLink",
        "name": "strCustArmorName",
    },
    "Helm": {
        "file": "strCustHelmFile",
        "link": "strCustHelmLink",
        "name": "strCustHelmName",
    },
    "Weapon": {
        "file": "strCustWeaponFile",
        "link": "strCustWeaponLink",
        "name": "strCustWeaponName",
    },
    "Pet": {
        "file": "strPetFile",
        "link": "strPetLink",
        "name": "strPetName",
    },
    "Cape": {
        "file": "strCustCapeFile",
        "link": "strCustCapeLink",
        "name": "strCustCapeName",
    },
}

async def start_server():

    global _server_started

    if _server_started:
        return

    app = web.Application()

    async def render_html(request):

        return web.FileResponse(HTML_PATH)

    async def testing2(request):

        return web.FileResponse(SWF_PATH)

    app.router.add_get("/render.hmtl", render_html)

    app.router.add_get("/testing2.swf", testing2)

    async def local_asset(request):

        path = request.match_info["path"]

        data = await fetch_asset(path)

        return web.Response(
            body=data,
            headers={
                "Access-Control-Allow-Origin": "*",
            },
        )

    app.router.add_get(
        "/game/gamefiles/{path:.*}",
        local_asset,
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(runner, "127.0.0.1", 8765)

    await site.start()

    _server_started = True

    print("Render server started")

def replace_item(
    flashvars: str,
    item_type: str,
    item_file: str,
    item_link: str = "",
    item_name: str = "",
    weapon_type: str = "",
):

    if item_type not in ITEM_FIELDS:
        raise ValueError(
            f"Invalid item type: {item_type}. "
            f"Expected: {', '.join(ITEM_FIELDS)}"
        )

    fields = dict(parse_qsl(flashvars.lstrip("&"), keep_blank_values=True))

    fields[ITEM_FIELDS[item_type]["file"]] = item_file
    fields[ITEM_FIELDS[item_type]["link"]] = item_link
    fields[ITEM_FIELDS[item_type]["name"]] = item_name
    if weapon_type != "":
        fields["strWeaponType"] = weapon_type

    return "&" + urlencode(fields)

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


async def fetch_asset(path: str):

    if path in ASSET_CACHE:
        return ASSET_CACHE[path]

    url = f"https://game.aq.com/game/gamefiles/{path}"

    session = await get_session()

    async with session.get(
        url,
        proxy=PROXY_SERVICE,
        headers=HEADERS,
    ) as resp:
        resp.raise_for_status()

        data = await resp.read()

        ASSET_CACHE[path] = data

        return data


async def setup_page(
    username: str,
    item_type: str | None = None,
    item_file: str | None = None,
    item_link: str | None = None,
    item_name: str | None = None,
):

    await start_server()

    weapon_type = ""
    if item_type in WEAPON_FIELDS:
        weapon_type = item_type
        item_type = "Weapon"

    flash_vars = await get_flashvars(username)

    if item_type:
        if not item_file:
            raise ValueError("item_file is required when item_type is specified")

        flash_vars = replace_item(
            flash_vars,
            item_type=item_type,
            item_file=item_file,
            item_link=item_link or "",
            item_name=item_name or "",
            weapon_type=weapon_type
        )

    driver = get_driver()

    encoded = quote(flash_vars)

    url = f"http://127.0.0.1:8765/render.hmtl?flashVars={encoded}"

    await run_blocking(driver.get, url)

    # AQW assets load slowly
    await asyncio.sleep(7)

    return driver


async def run_blocking(func, *args):
    return await asyncio.to_thread(func, *args)


async def render_png(
    username: str,
    name: str | None = None,
    file: str | None = None,
    link: str | None = None,
    type: str | None = None,
    package: str = "",
):

    driver = await setup_page(
        username,
        item_type=type,
        item_file=file,
        item_link=link,
        item_name=name,
    )

    canvas = await get_canvas(driver)

    # get the canvas as a PNG base64 string
    canvas_base64 = driver.execute_script(
        "return arguments[0].toDataURL('image/png').substring(21);", canvas
    )

    # decode
    png = base64.b64decode(canvas_base64)

    image = Image.open(BytesIO(png)).convert("RGBA")

    output = BytesIO()
    image = crop_image(image)
    image.save(output, format="PNG")

    output.seek(0)
    driver.quit()
    return output


async def render_welcome(username: str):

    driver = await setup_page(username)

    canvas = await get_canvas(driver)

    # get the canvas as a PNG base64 string
    canvas_base64 = driver.execute_script(
        "return arguments[0].toDataURL('image/png').substring(21);", canvas
    )

    # decode
    png = base64.b64decode(canvas_base64)

    image = Image.open(BytesIO(png)).convert("RGBA")

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
