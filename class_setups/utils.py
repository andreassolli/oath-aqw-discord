import csv
import re
from io import StringIO

import aiohttp

from config import BOSS_TO_SHEET, CLASS_IMAGES_SHEET, CLASSES_SHEET

_class_images: dict[str, str] = {}  # canonical_name → image_url

_sheet_cache: dict[str, list[dict[str, str]]] = {}
_class_index: dict[str, str] = {}  # key → canonical_name
_class_loadouts: dict[str, dict[str, str]] = {}  # canonical_name → loadout


async def build_class_image_index() -> None:
    global _class_images

    if _class_images:
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(CLASS_IMAGES_SHEET) as resp:
            resp.raise_for_status()
            text = await resp.text()

    reader = csv.reader(StringIO(text))

    for row in reader:
        if len(row) < 2:
            continue

        name = row[0].strip()
        url = row[1].strip()

        if not name:
            continue

        # Only store if a valid URL exists
        if "drive.google.com/file/d/" in url:
            file_id = url.split("/d/")[1].split("/")[0]
            url = f"https://lh3.googleusercontent.com/d/{file_id}"

            _class_images[name] = url


def _normalize(name: str) -> str:
    return re.sub(r"\s+", "", name).lower()


def _generate_abbreviation(name: str) -> str:
    words = name.split()
    return "".join(word[0] for word in words).lower()


def get_class_index() -> dict[str, str]:
    return _class_index


def clear_class_index() -> None:
    _class_index.clear()
    _class_loadouts.clear()
    _class_images.clear()


def get_class_loadouts() -> dict[str, dict[str, str]]:
    return _class_loadouts


def get_class_image(canonical: str) -> str | None:
    # Exact match
    if canonical in _class_images:
        return _class_images[canonical]

    # Case-insensitive fallback
    for name, url in _class_images.items():
        if name.lower() == "no class":
            return url

    return None


async def build_class_index() -> None:
    global _class_index, _class_loadouts

    if _class_index:
        return

    await build_class_image_index()

    for boss_name in BOSS_TO_SHEET.keys():
        rows = await get_boss_sheet(boss_name)

        for row in rows:
            raw_name = row.get("Name", "").strip()
            if not raw_name:
                continue

            class_names = [name.strip() for name in raw_name.split("/")]

            loadout = {
                "sword": row.get("Sword", ""),
                "class": row.get("Class", ""),
                "helm": row.get("Helm", ""),
                "cloak": row.get("Cloak", ""),
                "elixir": row.get("Elixir", ""),
                "tonic": row.get("Tonic", ""),
                "consumable": row.get("Consumable", ""),
            }

            for name in class_names:
                canonical = name
                normalized = _normalize(name)
                abbrev = _generate_abbreviation(name)

                _class_loadouts[canonical] = loadout
                _class_index[normalized] = canonical
                _class_index[abbrev] = canonical


async def _fetch_and_cache_boss_sheet(
    boss_name: str,
) -> list[dict[str, str]]:

    if boss_name not in BOSS_TO_SHEET:
        raise ValueError("Unknown boss")

    gid = BOSS_TO_SHEET[boss_name]
    url = f"{CLASSES_SHEET}{gid}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            text = await resp.text()

    reader = csv.DictReader(StringIO(text))
    rows: list[dict[str, str]] = [
        {k: (v or "") for k, v in row.items()} for row in reader
    ]

    _sheet_cache[boss_name] = rows
    return rows


async def get_boss_sheet(
    boss_name: str,
) -> list[dict[str, str]]:

    if boss_name in _sheet_cache:
        return _sheet_cache[boss_name]

    return await _fetch_and_cache_boss_sheet(
        boss_name,
    )


async def get_classes_for_boss(
    boss_name: str,
) -> dict[str, dict[str, str]]:

    rows = await get_boss_sheet(boss_name)

    results: dict[str, dict[str, str]] = {}

    for row in rows:
        raw_name = row.get("Name", "").strip()
        if not raw_name:
            continue

        # Split multiple classes separated by " / "
        class_names = [name.strip() for name in raw_name.split("/")]

        loadout = {
            "sword": row.get("Sword", ""),
            "class": row.get("Class", ""),
            "helm": row.get("Helm", ""),
            "cloak": row.get("Cloak", ""),
            "elixir": row.get("Elixir", ""),
            "tonic": row.get("Tonic", ""),
            "consumable": row.get("Consumable", ""),
        }

        for name in class_names:
            results[name] = loadout

    return results


async def get_class_across_bosses(
    class_name: str,
) -> dict[str, dict[str, str]]:

    normalized = class_name.strip().lower()
    results: dict[str, dict[str, str]] = {}

    for boss_name in BOSS_TO_SHEET.keys():
        rows = await get_boss_sheet(boss_name)

        for row in rows:
            if row.get("Name", "").strip().lower() == normalized:
                results[boss_name] = {
                    "sword": row.get("Sword", ""),
                    "class": row.get("Class", ""),
                    "helm": row.get("Helm", ""),
                    "cloak": row.get("Cloak", ""),
                    "elixir": row.get("Elixir", ""),
                    "tonic": row.get("Tonic", ""),
                    "consumable": row.get("Consumable", ""),
                }
                break

    return results


def clear_sheet_cache() -> None:
    _sheet_cache.clear()
