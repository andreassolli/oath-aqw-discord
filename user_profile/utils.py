import csv
from io import BytesIO, StringIO
from typing import Any

import aiohttp
import requests
from PIL import Image, ImageDraw

from config import AQW_BADGES, AQW_INVENTORY, WEAPON_SHEET

_weapon_name_cache: set[str] | None = None


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


async def fetch_avatar(url: str) -> Image.Image:
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Avatar fetch failed: {resp.status}")

            data = await resp.read()

    return Image.open(BytesIO(data)).convert("RGBA")


def circle_crop(img, size):
    img = img.resize((size, size))
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, size, size), fill=255)
    img.putalpha(mask)
    return img


async def get_weapon_names() -> set[str]:
    global _weapon_name_cache

    if _weapon_name_cache is not None:
        return _weapon_name_cache

    if WEAPON_SHEET is None:
        raise RuntimeError("Weapon sheet URL not configured")
    r = requests.get(WEAPON_SHEET)
    r.raise_for_status()

    csv_data = StringIO(r.text)
    reader = csv.DictReader(csv_data)

    _weapon_name_cache = {row["Name"] for row in reader}

    return _weapon_name_cache


async def get_weapon_count(ccid: str) -> int:
    url = f"{AQW_INVENTORY}{ccid}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            inventory = await resp.json()

    weapons_list = await get_weapon_names()
    name_set = set(weapons_list)
    if _weapon_name_cache:
        print("Weapon names loaded:", len(_weapon_name_cache))

    return sum(1 for item in inventory if item["strName"] in name_set)


async def get_class_count(ccid: str) -> int:
    url = f"{AQW_INVENTORY}{ccid}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            inventory = await resp.json()

    unique_classes: set[str] = set()

    for item in inventory:
        if item.get("strType") == "Class":
            class_name = item.get("strName")
            if class_name:
                unique_classes.add(class_name)

    return len(unique_classes)


async def get_epic_badges(ccid: str) -> int:
    url = f"{AQW_BADGES}{ccid}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            badges = await resp.json()

    return sum(1 for badge in badges if badge["sCategory"] == "Epic Hero")


async def get_total_badges(ccid: str) -> int:
    url = f"{AQW_BADGES}{ccid}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            badges = await resp.json()

    return len(badges)


async def founder_check(ccid: str) -> bool:
    url = f"{AQW_BADGES}{ccid}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            badges = await resp.json()

    return any(
        badge.get("sTitle") == "Founder" and badge.get("sCategory") == "Legendary"
        for badge in badges
    )


async def get_whale_badges(ccid: str) -> dict[str, int | bool]:
    url = f"{AQW_BADGES}{ccid}"
    badge_categories = {"HeroMart", "Support", "Exclusive"}
    pet_badges = {"15 Years Played", "AC Loyalty", "Member Loyalty"}
    ioda = await check_for_ioda(ccid)
    gifting_2021 = False
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            badges = await resp.json()
            whale_badges = sum(
                1 for badge in badges if badge["sCategory"] in badge_categories
            )
            upholder_badges = sum(
                1 for badge in badges if badge["sCategory"] == "Upholder"
            )
            platinum_badges = sum(
                1 for badge in badges if badge["sTitle"] in pet_badges
            )
            gifting_badges = sum(
                1 for badge in badges if "giftingtier7" in badge["sFileName"]
            )
            lower_gifting = any(
                "giftingtier4" in badge.get("sFileName", "") for badge in badges
            )
            medium_gifting = any(
                "giftingtier5" in badge.get("sFileName", "") for badge in badges
            )
            gifting_2021 = any(
                any(
                    tier in badge.get("sFileName", "").lower()
                    for tier in ("giftingtier3r1", "giftingtier4r1")
                )
                for badge in badges
            )
            if gifting_2021:
                gifting_badges += 1

    return {
        "whale_badges": whale_badges,
        "upholder_badges": upholder_badges,
        "platinum_badges": platinum_badges,
        "gifting_badges": gifting_badges,
        "lower_gifting": lower_gifting,
        "medium_gifting": medium_gifting,
        "ioda": ioda,
    }


BADGE_CATEGORIES = {
    "51% Weapons": {
        "51% Weapons I": 7,
        "51% Weapons II": 15,
        "51% Weapons III": 23,
        "51% Weapons IV": 30,
    },
    "Epic Journey": {
        "Epic Journey I": 16,
        "Epic Journey II": 23,
        "Epic Journey III": 30,
        "Epic Journey IV": 31,
    },
    "Achievement Badges": {
        "Achievement Badges I": 150,
        "Achievement Badges II": 300,
        "Achievement Badges III": 450,
        "Achievement Badges IV": 600,
    },
    "Class Collector": {
        "Class Collector I": 50,
        "Class Collector II": 100,
        "Class Collector III": 150,
        "Class Collector IV": 200,
    },
    "Whale": {
        "Whale I": 150,
        "Whale II": 200,
        "Whale III": 250,
        "Whale IV": 300,
    },
}


def get_badge_category(badge_name: str) -> str | None:
    normalized = badge_name.strip().lower()

    for category_name, badge_map in BADGE_CATEGORIES.items():
        for badge_key in badge_map.keys():
            if badge_key.lower() == normalized:
                return category_name

    return None


async def get_category_counts(ccid: str) -> dict[str, int | bool]:
    return {
        "51% Weapons": await get_weapon_count(ccid),
        "Epic Journey": await get_epic_badges(ccid),
        "Achievement Badges": await get_total_badges(ccid),
        "Class Collector": await get_class_count(ccid),
        "Whale": (await get_whale_badges(ccid))["whale_badges"],
    }


def get_highest_from_category(category: dict[str, int], count: int) -> str | None:
    # sort by requirement descending
    sorted_badges = sorted(category.items(), key=lambda x: x[1], reverse=True)

    for badge, requirement in sorted_badges:
        if count >= requirement:
            return badge

    return None


BADGE_DISPLAY_ORDER = [
    "Guild Founder",
    "AQW Founder",
    "Whale",
    "Epic Journey",
    "Achievement Badges",
    "Class Collector",
    "51% Weapons",
]


def sort_badges(badges: list[str]) -> list[str]:
    def badge_key(badge: str):
        if badge in ("Guild Founder", "AQW Founder"):
            return (BADGE_DISPLAY_ORDER.index(badge), 0)

        category = get_badge_category(badge)

        if category in BADGE_DISPLAY_ORDER:
            return (BADGE_DISPLAY_ORDER.index(category) + 1, badge)

        return (999, badge)

    return sorted(badges, key=badge_key)


async def check_for_ioda(ccid: str) -> bool:
    url = f"{AQW_INVENTORY}{ccid}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            inventory = await resp.json()

    return any(
        "Item of Digital Awesomeness" in item.get("strName") for item in inventory
    )


async def define_whale(ccid: str) -> str | None:
    whaling = await get_whale_badges(ccid)
    if (
        whaling["whale_badges"] >= 300
        and whaling["lower_gifting"]
        and whaling["medium_gifting"]
        and whaling["platinum_badges"] >= 2
        and (whaling["upholder_badges"] >= 8 or whaling["platinum_badges"] >= 3)
        and whaling["ioda"]
    ):
        return "Whale IV"
    elif (
        whaling["whale_badges"] >= 250
        and whaling["gifting_badges"] >= 1
        and whaling["platinum_badges"] >= 1
        and whaling["upholder_badges"] >= 4
    ):
        return "Whale III"
    elif (
        whaling["whale_badges"] >= 200
        and whaling["gifting_badges"] >= 1
        and whaling["upholder_badges"] >= 4
    ):
        return "Whale II"
    elif whaling["whale_badges"] >= 150 and whaling["upholder_badges"] >= 2:
        return "Whale I"
    else:
        return None
