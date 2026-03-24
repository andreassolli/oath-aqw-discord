import asyncio
import random

import aiohttp

from economy.generate_rocks import generate_rocks
from economy.inventory import generate_inventory
from economy.shop_generation import generate_shop
from extra_commands.wordle import choose_new_word
from extra_commands.wordle_share import generate_wordle_share
from firebase_client import db, firestore
from inventory.utils import add_item
from request_utils import get_session
from user_profile.utils import fetch_inventory
from user_verification.utils import fetch_aqw_profile

BANS_COLLECTION = "bans"


async def backfill_ccids():
    docs = db.collection(BANS_COLLECTION).stream()

    updated = 0

    for doc in docs:
        data = doc.to_dict() or {}

        # Skip if ccid already exists
        if "ccid" in data and data["ccid"] == data["username"]:
            print(data["ccid"])
            continue

    print(f"\nFinished. Updated {updated} documents.")


def get_all_users():
    docs = db.collection("users").stream()

    sorted_users = []

    for doc in docs:
        data = doc.to_dict() or {}
        ccid = data.get("ccid")

        if ccid:
            sorted_users.append(
                {"ccid": int(ccid), "username": data.get("aqw_username")}
            )

    sorted_users.sort(key=lambda x: x["ccid"])
    print(sorted_users)


def migrate_inventory():
    users_ref = db.collection("users")
    docs = users_ref.stream()

    updated_count = 0

    for doc in docs:
        data = doc.to_dict() or {}

        inventory = data.get("inventory")
        if not inventory:
            continue

        changed = False

        for item in inventory:
            item_id = item.get("id")

            if item_id == "Red Card":
                if item.get("image") != "red_card.png":
                    item["image"] = "red_card.png"
                    item["display"] = "red_card_item.png"
                    changed = True

            elif item_id == "Test Border":
                if item.get("image") != "test_border.png":
                    item["image"] = "test_border.png"
                    item["display"] = "test_border_item.png"
                    changed = True

        if changed:
            doc.reference.update({"inventory": inventory})
            updated_count += 1
            print(f"Updated user {doc.id}")

    print(f"Done. Updated {updated_count} users.")


ITEM_DATA = {
    "Red Card": {
        "image": "red_card.png",
        "display": "red_card_item.png",
    },
    "Test Border": {
        "image": "test_border.png",
        "display": "test_border_item.png",
    },
}


def migrate_test_border_to_doom():
    users_ref = db.collection("users")
    docs = users_ref.stream()

    updated_count = 0

    for doc in docs:
        data = doc.to_dict() or {}
        updates = {}

        # -------------------
        # Handle equipped border
        # -------------------
        border = data.get("border")

        if isinstance(border, dict) and border.get("id") == "Test Border":
            updates["border"] = {
                "id": "Doom Border",
                "display": "doom_border_item.png",
                "image": "doom_border.png",
                "type": "border",
            }

        # -------------------
        # Handle inventory
        # -------------------
        inventory = data.get("inventory", [])
        new_inventory = []
        inventory_changed = False

        for item in inventory:
            if (
                isinstance(item, dict)
                and item.get("id") == "Test Border"
                and item.get("type") == "border"
            ):
                new_inventory.append(
                    {
                        "id": "Doom Border",
                        "display": "doom_border_item.png",
                        "image": "doom_border.png",
                        "type": "border",
                    }
                )
                inventory_changed = True
            else:
                new_inventory.append(item)

        if inventory_changed:
            updates["inventory"] = new_inventory

        # -------------------
        # Apply updates
        # -------------------
        if updates:
            doc.reference.update(updates)
            updated_count += 1
            print(f"Updated user {doc.id}")

    print(f"Done. Updated {updated_count} users.")


async def test_fetch_call():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://game.aq.com/game/api/data/servers") as response:
            print(await response.text())
            import random

            from firebase_admin import firestore

            from firebase_client import db


def migrate_points_to_gems():
    users_ref = db.collection("users")
    docs = users_ref.stream()

    updated_count = 0

    for doc in docs:
        data = doc.to_dict() or {}

        points = data.get("points", 0)
        if points <= 0:
            continue

        # ✅ NEW: track already rewarded points
        last_awarded = data.get("gems_awarded_points", 0)

        new_points = points - last_awarded
        chunks = new_points // 15

        if chunks <= 0:
            continue

        # total gems to award
        gems_to_add = sum(random.randint(1, 3) for _ in range(chunks))

        # update awarded points safely
        awarded_points = last_awarded + (chunks * 15)

        doc.reference.update(
            {
                "gems": firestore.Increment(gems_to_add),
                "gems_awarded_points": awarded_points,
            }
        )

        updated_count += 1
        print(
            f"{doc.id}: +{gems_to_add} gems "
            f"(points={points}, new={new_points}, tracked={awarded_points})"
        )

    print(f"Done. Updated {updated_count} users.")


from firebase_client import db


def ensure_currency_fields():
    users_ref = db.collection("users")
    docs = users_ref.stream()

    updated_count = 0

    for doc in docs:
        data = doc.to_dict() or {}

        updates = {}

        if "gems" not in data:
            updates["gems"] = 0

        if "coins" not in data:
            updates["coins"] = 0

        if updates:
            doc.reference.update(updates)
            updated_count += 1
            print(f"Updated {doc.id}: {updates}")

    print(f"Done. Updated {updated_count} users.")


if __name__ == "__main__":
    generate_rocks()
    # get_all_users()
    # choose_new_word()
# asyncio.run(
#    add_item(
#        "292040660696039424", "Guts Card", "card", "guts_card.png", "custom.png"
#    )
# )
# asyncio.run(test_fetch_call())
# asyncio.run(generate_inventory(userId="292040660696039424"))
# asyncio.run(backfill_ccids())
# asyncio.run(generate_wordle_share(None, "292040660696039424"))
