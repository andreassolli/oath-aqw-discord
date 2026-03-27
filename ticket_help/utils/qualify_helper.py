import asyncio
import time

from aiohttp import ClientResponseError

from config import AQW_BADGES, AQW_INVENTORY

CONCURRENCY_LIMIT = 3

BATCH_SIZE = 400
MAX_RETRIES = 5
REQUESTS_PER_SECOND = 0.3

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
]


class SteadyRateLimiter:
    def __init__(self, rate_per_second: float):
        self.delay = 1 / rate_per_second
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def wait(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last

            if elapsed < self.delay:
                await asyncio.sleep(self.delay - elapsed)

            self._last = time.monotonic()


async def verify_helper(session, limiter, ccid: str) -> dict:
    inventory_url = f"{AQW_INVENTORY}{ccid}"
    badge_url = f"{AQW_BADGES}{ccid}"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            await limiter.wait()

            inventory_task = session.get(inventory_url)
            badge_task = session.get(badge_url)

            inventory_resp, badge_resp = await asyncio.gather(
                inventory_task, badge_task
            )

            # Handle rate limits
            if inventory_resp.status == 429 or badge_resp.status == 429:
                raise ClientResponseError(
                    inventory_resp.request_info,
                    inventory_resp.history,
                    status=429,
                    message="Rate limited",
                )

            inventory_resp.raise_for_status()
            badge_resp.raise_for_status()

            inventory = await inventory_resp.json()
            badges = await badge_resp.json()

            badge = any("Blade of Awe" in item["sTitle"] for item in badges)

            weapon = any(
                weapon in item["strName"] for item in inventory for weapon in WEAPONS
            )
            classes = any(
                class_name in item["strName"]
                for item in inventory
                for class_name in CLASSES
            )
            taunt = any("Scroll of Enrage" in item["strName"] for item in inventory)
            potion = any(
                potion in item["strName"] for item in inventory for potion in POTIONS
            )
            qualified = weapon and classes and taunt and potion
            return {
                "qualified": qualified,
                "weapon": weapon,
                "classes": classes,
                "taunt": taunt,
                "potion": potion,
                "blade of awe": badge,
            }

        except ClientResponseError as e:
            if e.status == 429:
                wait_time = 2**attempt
                await asyncio.sleep(wait_time)
            else:
                raise

    raise Exception(f"Max retries exceeded for {ccid}")
