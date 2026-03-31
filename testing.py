import asyncio
import random

import aiohttp
from google.cloud import firestore as gc_firestore

from economy.generate_rocks import generate_rocks
from economy.inventory import generate_inventory
from economy.shop_generation import generate_shop
from extra_commands.wordle import choose_new_word
from extra_commands.wordle_share import generate_wordle_share
from firebase_client import db, firestore
from inventory.utils import add_item
from request_utils import get_session
from user_profile.computer_border_test import apply_computer_border
from user_profile.image_test import generate_test_card
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


async def find_users_with_doom_card():
    users = db.collection("users").stream()

    found = []

    for doc in users:
        data = doc.to_dict()

        inventory = data.get("inventory") or []  # ✅ FIX

        if any(item.get("id") == "Doom Card" for item in inventory):
            name = data.get("aqw_username")
            found.append((doc.id, name))

    print(f"Found {len(found)} users with Doom Card.\nUsers: {found}")
    return found


def migrate_counting_score():
    users_ref = db.collection("users")

    BATCH_LIMIT = 500
    batch = db.batch()
    operation_count = 0
    updated_count = 0

    docs = users_ref.stream()

    for doc in docs:
        data = doc.to_dict() or {}
        doc_ref = doc.reference  # safer

        # Skip if field doesn't exist
        if "message_count" not in data:
            continue

        message_count = data.get("message_count") or 0
        counting_score = data.get("counting_score") or 0

        # Ensure integers (prevents crashes if corrupted data)
        try:
            message_count = int(message_count)
            counting_score = int(counting_score)
        except (ValueError, TypeError):
            print(f"Skipping {doc.id} invalid data")
            continue

        # Skip unnecessary updates
        if message_count == 0:
            batch.update(doc_ref, {"message_count": gc_firestore.DELETE_FIELD})
        else:
            new_score = counting_score + message_count

            batch.update(
                doc_ref,
                {
                    "counting_score": new_score,
                    "message_count": gc_firestore.DELETE_FIELD,
                },
            )

        operation_count += 1
        updated_count += 1

        print(f"{doc.id}: {counting_score} + {message_count} → updated")

        # Commit batch safely
        if operation_count >= BATCH_LIMIT:
            batch.commit()
            batch = db.batch()
            operation_count = 0

    # Final commit
    if operation_count > 0:
        batch.commit()

    print(f"Migration complete ✅ Updated {updated_count} users")


def backfill_wordle_stats():
    games_ref = db.collection("wordle_games")
    docs = games_ref.stream()

    updated = 0

    for doc in docs:
        data = doc.to_dict() or {}
        doc_ref = doc.reference

        # Skip if already migrated (IMPORTANT)
        if data.get("stats_recorded"):
            continue

        if not data.get("completed"):
            continue

        guess_count = data.get("guess_count", 0)
        won = data.get("won", False)

        try:
            guess_count = int(guess_count)
        except (ValueError, TypeError):
            print(f"Skipping {doc.id} بسبب invalid data")
            continue

        guesses_used = guess_count if won else 7

        doc_ref.update(
            {
                "total_guesses": guesses_used,
                "games_played": 1,
                "stats_recorded": True,  # ✅ prevents double counting
            }
        )

        updated += 1
        print(f"{doc.id}: initialized with {guesses_used} guesses")

    print(f"Done. Updated {updated} users.")


def migrate_shop_prices():
    items_ref = db.collection("shop_items")
    docs = items_ref.stream()

    batch = db.batch()
    count = 0

    for doc in docs:
        data = doc.to_dict()
        ref = doc.reference

        price = data.get("price", 0)
        currency = data.get("currency", "coins")

        # Normalize currency
        if currency == "gem":
            currency = "gems"

        # Convert to new format
        coin_price = 0
        shard_price = 0

        if currency == "coins":
            coin_price = price
        elif currency == "gems":
            shard_price = price

        # Prepare update
        update_data = {
            "coin_price": coin_price,
            "shard_price": shard_price,
            "price": gc_firestore.DELETE_FIELD,
            "currency": gc_firestore.DELETE_FIELD,
        }

        batch.update(ref, update_data)
        count += 1

        # Firestore batch limit
        if count % 500 == 0:
            batch.commit()
            batch = db.batch()

    if count % 500 != 0:
        batch.commit()

    print(f"Migrated {count} shop items.")


if __name__ == "__main__":
    asyncio.run(generate_test_card())
    # migrate_shop_prices()
    # backfill_wordle_stats()
    # asyncio.run(find_users_with_doom_card())
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
