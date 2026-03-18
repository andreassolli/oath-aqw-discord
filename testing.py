import asyncio

import aiohttp

from economy.inventory import generate_inventory
from economy.shop_generation import generate_shop
from extra_commands.wordle import choose_new_word
from extra_commands.wordle_share import generate_wordle_share
from firebase_client import db
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


def migrate_equipped_items():
    users_ref = db.collection("users")
    docs = users_ref.stream()

    updated_count = 0

    for doc in docs:
        data = doc.to_dict() or {}

        updates = {}

        # Handle border
        border = data.get("border")
        if isinstance(border, str) and border in ITEM_DATA:
            updates["border"] = {
                "id": border,
                **ITEM_DATA[border],
            }

        # Handle card
        card = data.get("card")
        if isinstance(card, str) and card in ITEM_DATA:
            updates["card"] = {
                "id": card,
                **ITEM_DATA[card],
            }

        if updates:
            doc.reference.update(updates)
            updated_count += 1
            print(f"Updated user {doc.id}")

    print(f"Done. Updated {updated_count} users.")


async def test_fetch_call():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://game.aq.com/game/api/data/servers") as response:
            print(await response.text())


if __name__ == "__main__":
    # get_all_users()
    choose_new_word()
# asyncio.run(
#    add_item(
#        "292040660696039424", "Guts Card", "card", "guts_card.png", "custom.png"
#    )
# )
# asyncio.run(test_fetch_call())
# asyncio.run(generate_inventory(userId="292040660696039424"))
# asyncio.run(backfill_ccids())
# asyncio.run(generate_wordle_share(None, "292040660696039424"))
