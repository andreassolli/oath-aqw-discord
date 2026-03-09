import asyncio
import logging

import aiohttp
from bs4 import BeautifulSoup
from firebase_admin import firestore

from firebase_client import db
from user_profile.utils import fetch_badges

logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def normalize(title: str) -> str:
    return title.strip().lower()


CONCURRENT_REQUESTS = 3


async def sync_badges_full():
    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS)

    badge_map = {}

    async with aiohttp.ClientSession(connector=connector) as session:

        async def process(i):
            url = f"http://aqwwiki.wikidot.com/charpage:{i}"
            scraped = await make_api_call(session, url)

            if scraped:
                print(f"Found page {i}")

            if not scraped or not scraped.get("image_alt"):
                return

            if scraped["is_legendary"] or scraped["is_ae"]:
                return

            filename = normalize_filename(scraped["image_alt"])
            badge_map[filename] = {
                "name": scraped["name"],
                "requirements": scraped["requirements"],
                "is_special_offer": scraped["is_special_offer"],
                "is_pseudo_rare": scraped["is_pseudo_rare"],
                "is_rare": scraped["is_rare"],
                "is_heromart": scraped["is_heromart"],
            }

        tasks = [process(i) for i in range(800)]
        await asyncio.gather(*tasks)

    db.collection("badge_metadata").document("all").set(
        {"badges": badge_map, "last_updated": firestore.SERVER_TIMESTAMP}
    )

    print("✅ Badge metadata synced.")
    print(f"Total stored: {len(badge_map)}")


def parse_badge_page(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    result = {
        "name": None,
        "image_alt": None,
        "is_rare": False,
        "requirements": None,
        "is_special_offer": False,
        "is_pseudo_rare": False,
        "is_legendary": False,
        "is_ae": False,
        "is_heromart": False,
    }

    # Badge name
    imgs = soup.select("#page-content img")
    for img in imgs:
        src = img.get("src", "")
        if "badges" in src:
            result["image_alt"] = img.get("alt")
            break

    # Title
    title = soup.select_one("#page-title")
    if title:
        result["name"] = title.get_text(strip=True)

    # Check if rare via tags (most reliable)
    tags_div = soup.find("div", class_="page-tags")
    if tags_div:
        tags = [a.get_text(strip=True).lower() for a in tags_div.find_all("a")]
        result["is_rare"] = "rare" in tags
        result["is_pseudo_rare"] = "pseudo-rare" in tags
        result["is_special_offer"] = "specialoffer" in tags
        result["is_legendary"] = "cp-legendary" in tags
        result["is_ae"] = "cp-ae" in tags
        result["is_heromart"] = "cp-heromart" in tags

    # Extract requirements
    requirements_label = soup.find("p", string=lambda s: s and "Requirements:" in s)

    if requirements_label:
        next_p = requirements_label.find_next("p")
        if next_p:
            result["requirements"] = next_p.get_text(strip=True)

    return result


async def make_api_call(session: aiohttp.ClientSession, url: str):
    async with session.get(url, headers=HEADERS) as response:
        if response.status != 200:
            return None

        html = await response.text()

        badge_data = parse_badge_page(html)

        return badge_data


def normalize_filename(name: str | None) -> str | None:
    if not name:
        return None
    return name.strip().lower()


async def run():
    user_ref = db.collection("users").document("192864801595064321")
    doc = user_ref.get()

    ccid = doc.to_dict().get("ccid") if doc.exists else None
    if not ccid:
        print("No CCID found.")
        return

    badges = await fetch_badges(ccid)
    api_titles = {
        normalize_filename(b["sFileName"]) for b in badges if b.get("sFileName")
    }
    metadata_doc = db.collection("badge_metadata").document("all").get()

    if not metadata_doc.exists:
        print("Badge metadata not synced yet.")
        return

    badge_map = metadata_doc.to_dict()["badges"]

    missing_badges = []

    for filename, data in badge_map.items():
        if filename == normalize_filename("charbadge-17thBirthdayCollection.jpg"):
            filename = normalize_filename("charbadge-17thBirthdayCollection2.jpg")
        if data["is_rare"]:
            continue
        if data["is_pseudo_rare"] and data["is_heromart"]:
            continue
        if filename not in api_titles:
            missing_badges.append(data)

    print("\n=== MISSING BADGES ===")

    for badge in missing_badges:
        print(f"Name: {badge['name']}")

    print(f"\nTotal missing: {len(missing_badges)}")


if __name__ == "__main__":
    asyncio.run(run())

# Requirements: {badge["requirements"]}
# Special Offer: {badge["is_special_offer"]}
# Pseudo Rare: {badge["is_pseudo_rare"]}
