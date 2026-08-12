from datetime import datetime, timedelta
from typing import Optional
from collections import Counter
import discord
from firebase_admin import firestore
from firebase_client import db
DIFFICULTY_MAP = {
    "easy": "🟢⚫️⚫️⚫️",
    "medium": "🟠🟠⚫️⚫️",
    "hard": "🔴🔴🔴⚫️",
    "very hard": "🟣🟣🟣🟣"
}


POTIONS = [
    "Fate",
    "Battle",
    "Might",
    "Sage",
    "Malevolence",
    "Malice",
    "Honor",
    "Philtre",
]

WEAPONS = [
    "Burning Sword of Doom",
    "Dual Exalted Apotheosis",
    "Dual Necrotic Swords of Doom",
    "Empowered BladeMaster's Katana",
    "Empowered Bloodletter",
    "Empowered Caladbolg",
    "Empowered Charged Oblivion Blade",
    "Empowered Dual Caladbolgs",
    "Empowered Dual Hollowborn Caladbolgs",
    "Empowered Dual Katanas",
    "Empowered Higure",
    "Empowered Hollowborn Caladbolg",
    "Empowered Oblivion Blade",
    "Empowered Overfiend Blade",
    "Empowered Prismatic Manslayer",
    "Empowered Prismatic Manslayers",
    "Empowered Shadow Spear",
    "Empowered Sole Bloodletter",
    "Empowered Ungodly Reavers",
    "Exalted Apotheosis",
    "Gramiel's Divine Enoch",
    "Greatblade of the Entwined Eclipse",
    "Hollowborn Sword of Doom",
    "Malgor's ShadowFlame Blade",
    "Necrotic Blade of Doom",
    "Necrotic Blade of the Underworld",
    "Necrotic Sword of Doom",
    "Necrotic Sword of the Abyss",
    "Providence",
    "Sin of the Abyss",
    "Sin Of The Underworld",
    "Star Light of the Empyrean",
    "Star Lights of the Empyrean",
]

CLASSES = [
    "Lord of Order",
    "ArchPaladin",
    "Chrono ShadowHunter",
    "Chrono ShadowSlayer",
    "Verus DoomKnight",
    "Legion Revenant",
    "StoneCrusher",
    "Infinity Titan",
    "Dragon of Time"
]
CLASS_BADGES = {
    "Verus DoomKnight",
    "Chaos Avenger",
    "Legion Revenant",
    "Void Highlord",
    "Dragon of Time",
    "King's Echo",
}
BADGES_TO_FIND = {
    "Blade of Awe",
    "Awe Ascension",
    "Radiant Goddess Of War",
}

def sort_badges(badges: list[dict]):
    others = {
        item["sTitle"]
        for item in badges
        if any(badge in item["sTitle"] for badge in BADGES_TO_FIND)
    }

    class_badges = {
        item["sTitle"]
        for item in badges
        if any(badge in item["sTitle"] for badge in CLASS_BADGES)
    }

    return {"class_badges": class_badges, "others": others}


def sort_inventory(inventory: list[dict]):
    weapons = Counter(
        item["strName"]
        for item in inventory
        if any(weapon in item["strName"] for weapon in WEAPONS)
    )

    taunt = next(
        (
            item["intCount"]
            for item in inventory
            if item["strName"] == "Scroll of Enrage"
        ),
        0,
    )

    classes = {
        class_name
        for item in inventory
        for class_name in CLASSES
        if class_name in item["strName"]
    }

    potions = {
        item["strName"]: item["intCount"]
        for item in inventory
        if any(potion in item["strName"] for potion in POTIONS)
    }

    return {
        "weapons": weapons,
        "classes": classes,
        "potions": potions,
        "taunt": taunt,
    }

def get_week_start(dt: datetime):
    # Monday start (ISO week)
    return dt - timedelta(days=dt.weekday())


def set_active_ticket(user_id: int, ticket_name: str):
    user_ref = db.collection("users").document(str(user_id))
    user_ref.set({"active_ticket": ticket_name}, merge=True)


def clear_active_ticket(user_id: int, ticket_name: Optional[str] = None):

    user_ref = db.collection("users").document(str(user_id))
    doc = user_ref.get()

    if not doc.exists:
        return

    data = doc.to_dict() or {}

    if ticket_name is None or data.get("active_ticket") == ticket_name:
        user_ref.update({"active_ticket": firestore.DELETE_FIELD})


async def find_guide_threads(
    guild: discord.Guild,
    guide_channel_id: int,
    bosses: list[str],
) -> dict[str, discord.Thread]:
    """
    Returns {boss_name: thread} for matched guide threads.
    """
    channel = guild.get_channel(guide_channel_id)
    if not channel:
        return {}

    matches: dict[str, discord.Thread] = {}
    bosses_lower = [b.lower() for b in bosses]

    # Active threads
    threads = list(channel.threads)

    # Archived threads (important!)
    async for thread in channel.archived_threads(limit=100):
        threads.append(thread)

    for thread in threads:
        title = thread.name.lower()
        for boss, boss_l in zip(bosses, bosses_lower):
            if boss_l in title and boss not in matches:
                matches[boss] = thread

    return matches
