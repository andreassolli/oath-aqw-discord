import csv
from datetime import timedelta
from io import BytesIO, StringIO
from typing import Any

import aiohttp
import discord
from google.cloud.firestore_v1 import FieldFilter
from PIL import Image, ImageDraw

from config import AQW_BADGES, AQW_INVENTORY, WEAPON_SHEET
from firebase_client import db
from http_client import get_session
from request_utils import rate_limited_get_json

_weapon_name_cache: set[str] | None = None


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


async def fetch_badges(ccid: str) -> list[dict]:
    url = f"{AQW_BADGES}{ccid}"
    return await rate_limited_get_json(url)


async def fetch_inventory(ccid: str) -> list[dict]:
    url = f"{AQW_INVENTORY}{ccid}"
    return await rate_limited_get_json(url)


async def fetch_avatar(url: str) -> Image.Image:
    timeout = aiohttp.ClientTimeout(total=10)

    session = await get_session()
    async with session.get(url, timeout=timeout) as resp:
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


def rounded_crop(img, size, radius):
    img = img.resize((size, size))

    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)

    # Draw rounded rectangle instead of circle
    draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=255)

    img.putalpha(mask)
    return img


async def get_weapon_names() -> set[str]:
    global _weapon_name_cache

    if _weapon_name_cache is not None:
        return _weapon_name_cache

    if WEAPON_SHEET is None:
        raise RuntimeError("Weapon sheet URL not configured")

    session = await get_session()

    async with session.get(WEAPON_SHEET) as resp:
        resp.raise_for_status()
        text = await resp.text()

    csv_data = StringIO(text)
    reader = csv.DictReader(csv_data)

    _weapon_name_cache = {row["Name"].lower() for row in reader if row.get("Name")}

    return _weapon_name_cache


async def calculate_weapon_count(inventory: list[dict]) -> int:
    weapons_list = await get_weapon_names()
    name_set = set(weapons_list)
    if _weapon_name_cache:
        print("Weapon names loaded:", len(_weapon_name_cache))

    for item in inventory:
        if item["strName"].lower() in name_set:
            print(item["strName"])

    return sum(1 for item in inventory if item["strName"].lower() in name_set)


async def calculate_class_count(inventory: list[dict]) -> int:

    unique_classes: set[str] = set()

    for item in inventory:
        if item.get("strType") == "Class":
            class_name = item.get("strName")
            if class_name:
                unique_classes.add(class_name)

    return len(unique_classes)


def calculate_epic_badges(badges: list[dict]) -> int:
    return sum(1 for badge in badges if badge.get("sCategory") == "Epic Hero")


def calculate_total_badges(badges: list[dict]) -> int:
    return len(badges)


def calculate_founder(badges: list[dict]) -> bool:

    founder_titles = {"Founder", "Beta Tester"}

    return any(
        badge.get("sCategory") == "Legendary" and badge.get("sTitle") in founder_titles
        for badge in badges
    )


def calculate_whale_badges(badges: list[dict]) -> dict:

    badge_categories = {"HeroMart", "Support", "Exclusive"}

    pet_badges = {"15 Years Played", "AC Loyalty", "Member Loyalty"}

    whale_badges = sum(
        1 for badge in badges if badge.get("sCategory") in badge_categories
    )

    upholder_badges = sum(
        1 for badge in badges if "Upholder" in badge.get("sTitle", "")
    )

    platinum_badges = sum(1 for badge in badges if badge.get("sTitle") in pet_badges)

    gifting_badges = sum(
        1 for badge in badges if "giftingtier7" in badge.get("sFileName", "")
    )

    lower_gifting = any(
        "giftingtier4" in badge.get("sFileName", "") for badge in badges
    )

    medium_gifting = any(
        "giftingtier5" in badge.get("sFileName", "") for badge in badges
    )

    gifting_2021 = any(
        tier in badge.get("sFileName", "").lower()
        for badge in badges
        for tier in ("giftingtier3r1", "giftingtier4r1")
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


async def get_badge_stats(ccid: str) -> dict:

    badges = await fetch_badges(ccid)

    return {
        "total_badges": calculate_total_badges(badges),
        "epic_badges": calculate_epic_badges(badges),
        "founder": calculate_founder(badges),
        **whale,
    }


async def get_inventory_stats(ccid: str) -> dict:

    inventory = await fetch_inventory(ccid)

    class_count = await calculate_class_count(inventory)

    return {
        "total_items": len(inventory),
        "unique_classes": class_count,
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


async def check_for_ioda(inventory: list[dict]) -> bool:

    return any(
        "Item of Digital Awesomeness" in item.get("strName", "") for item in inventory
    )


def define_whale(badges: list[dict], ioda: bool) -> str | None:

    whaling = calculate_whale_badges(badges)
    print("Upholder badges:", whaling["upholder_badges"])
    print("Platinum badges:", whaling["platinum_badges"])
    print("Gifting badges:", whaling["gifting_badges"])
    if (
        whaling["whale_badges"] >= 300
        and whaling["lower_gifting"]
        and whaling["medium_gifting"]
        and whaling["platinum_badges"] >= 2
        and (whaling["upholder_badges"] >= 8 or whaling["platinum_badges"] >= 3)
        and ioda
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
        and whaling["upholder_badges"] >= 3
    ):
        return "Whale II"

    elif whaling["whale_badges"] >= 150 and whaling["upholder_badges"] >= 2:
        return "Whale I"

    return None
