import asyncio
import random
from datetime import datetime

import aiohttp
import discord
import requests
from google.cloud import firestore as gc_firestore
from tweepy import Client as TwitterClient

from economy.generate_rocks import generate_rocks
from economy.inventory import generate_inventory
from economy.shop_generation import generate_shop
from extra_commands.twitter import check_twitter
from extra_commands.wordle import choose_new_word
from extra_commands.wordle_share import generate_wordle_share
from firebase_client import db, firestore
from inventory.utils import add_item
from request_utils import get_session
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


def reset_coins():
    users_ref = db.collection("users")
    docs = users_ref.stream()

    batch = db.batch()
    count = 0

    for doc in docs:
        ref = doc.reference

        # Prepare update
        update_data = {
            "gems": 0,
            "coins": 0,
        }

        batch.update(ref, update_data)
        count += 1

        # Firestore batch limit
        if count % 500 == 0:
            batch.commit()
            batch = db.batch()

    if count % 500 != 0:
        batch.commit()

    print(f"Done. Updated {count} users.")


BATCH_LIMIT = 500


def migrate_quest_names_batch():
    users_ref = db.collection("users").stream()

    batch = db.batch()
    operation_count = 0
    updated_count = 0

    for user_doc in users_ref:
        user_data = user_doc.to_dict()
        quests_completed = user_data.get("quests_completed")

        if not quests_completed:
            continue

        updated_quests = []
        changed = False

        for quest in quests_completed:
            if quest == "quest_1":
                updated_quests.append("Weekly 1")
                changed = True
            elif quest == "quest_2":
                updated_quests.append("Weekly 2")
                changed = True
            else:
                updated_quests.append(quest)

        if not changed:
            continue

        # Add update to batch
        batch.update(user_doc.reference, {"quests_completed": updated_quests})

        operation_count += 1
        updated_count += 1

        # Commit batch when limit reached
        if operation_count >= BATCH_LIMIT:
            batch.commit()
            print(f"✅ Committed {operation_count} updates")

            # Reset batch
            batch = db.batch()
            operation_count = 0

    # Commit any remaining operations
    if operation_count > 0:
        batch.commit()
        print(f"✅ Committed final {operation_count} updates")

    print(f"🎉 Migration complete. Updated {updated_count} users.")


def get_total_points():
    snapshot_ref = db.collection("points_archive").document("2026-04-01_16-02-50")
    snapshot_doc = snapshot_ref.get()

    snapshot2_ref = db.collection("points_archive").document("2026-03-01_22-10-54")
    snapshot2_doc = snapshot2_ref.get()

    if not snapshot_doc.exists or not snapshot2_doc.exists:
        print("One or both snapshots not found.")
        return

    snapshot_users = snapshot_doc.to_dict().get("users", {})
    snapshot2_users = snapshot2_doc.to_dict().get("users", {})

    updated = 0
    skipped = 0

    batch = db.batch()
    batch_count = 0

    all_user_ids = set(snapshot_users.keys()) | set(snapshot2_users.keys())

    for user_id in all_user_ids:
        snapshot_points = snapshot_users.get(user_id, {}).get("tickets_claimed", 0)
        snapshot2_points = snapshot2_users.get(user_id, {}).get("tickets_claimed", 0)

        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            skipped += 1
            continue

        user_data = user_doc.to_dict() or {}
        current_points = user_data.get("tickets_claimed", 0)

        total_snapshot_points = snapshot_points + snapshot2_points
        new_awarded = current_points + total_snapshot_points

        print(
            f"{user_id}: snap1={snapshot_points}, snap2={snapshot2_points}, "
            f"current={current_points}, total={new_awarded}"
        )

        batch.update(user_ref, {"total_claimed": new_awarded})

        batch_count += 1
        updated += 1

        if batch_count >= BATCH_LIMIT:
            batch.commit()
            print(f"Committed {batch_count} updates...")
            batch = db.batch()
            batch_count = 0

    if batch_count > 0:
        batch.commit()
        print(f"Committed final {batch_count} updates...")

    print("\nDone.")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")


async def add_killer_card():
    await add_item(
        str(463869761625915393),
        "Killer Card",
        "card",
        "killer_card.png",
        "killer_card_item.png",
        "rare",
    )


donations = [
    {"amount": 25, "name": "Isocat", "date": "2026-04-18"},
    {"amount": 10, "name": "Quincy Dao", "date": "2026-04-18"},
    {"amount": 5, "name": "Samdal", "date": "2026-04-18"},
    {"amount": 1, "name": "Smoked Out", "date": "2026-04-18"},
    {"amount": 10, "name": "Smoked Out", "date": "2026-04-20"},
    {"amount": 10, "name": "Groot", "date": "2026-04-21"},
    {"amount": 50, "name": "Isocat", "date": "2026-04-23"},
    {"amount": 100, "name": "Skyper", "date": "2026-04-24"},
    {"amount": 50, "name": "Greed", "date": "2026-04-24"},
    {"amount": 50, "name": "Redact", "date": "2026-04-24"},
    {"amount": 50, "name": "Thundersnow Demigod", "date": "2026-04-24"},
    {"amount": 50, "name": "Smoked Out", "date": "2026-04-24"},
    {"amount": 50, "name": "Groot", "date": "2026-04-25"},
    {"amount": 20, "name": "Groot", "date": "2026-04-25"},
    {"amount": 100, "name": "Im Clancy", "date": "2026-04-25"},
]


async def backlog_donations():
    for donation in donations:
        timestamp = datetime.strptime(donation["date"], "%Y-%m-%d").isoformat() + "Z"

        payload = {
            "embeds": [
                {
                    "title": "New donation!",
                    "description": (
                        f"**{donation['name']}** has donated "
                        f"${donation['amount']} to the Oath Ko-Fi ❤️"
                    ),
                    "timestamp": timestamp,
                    "footer": {"text": "Thank you for supporting Oath ❤️"},
                }
            ]
        }

        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

        if response.ok:
            print(f"Sent: {donation['name']} (${donation['amount']})")
        else:
            print(
                f"Failed: {donation['name']} ({response.status_code}) {response.text}"
            )


async def post_kofi_summary():
    timestamp = datetime.now().isoformat() + "Z"

    payload = {
        "embeds": [
            {
                "title": "Oath Ko-Fi April '26 ☕️",
                "description": (
                    "We want to be as open and transparent about the fundings, as well as spendings, for our community. "
                    "In order to do so we will be posting a summary each month of inventory, donations received, and prizes spent.\n\n"
                    "**Donations received 💵**\n"
                    "- Total: **$1046**\n"
                    "- After fees: **$935**\n\n"
                    "**Total spendings 💸**\n"
                    "- Total: **$943**, $8 above\n\n"
                    "**Expenses 🧾**\n"
                    "- Hosting expense, April/May: **$26**\n"
                    "- Pay artists: **$22**\n"
                    "- Set aside for commission: **$50**\n\n"
                    "**Inventory 🧳**\n"
                    "```diff\n"
                    "+ 73 000 Artix Points ($365)\n"
                    "+ 23 HeroPoints ($55)\n"
                    "+ 11 HeroMart Items ($276)\n"
                    "+ 6 AQW:I Founder ($150)\n"
                    "```\n"
                    "Stay tuned for when we will distribute some of the prizes acquired! "
                    "<a:Twilly_fire:1457144099432825095>"
                ),
                "color": 0x34B4EB,
                "timestamp": timestamp,
                "footer": {
                    "text": "A massive thank you to everyone who supported us this month ❤️"
                },
            }
        ]
    }

    response = requests.post(
        "https://discord.com/api/webhooks/1497599199188094977/3rZftx-W9mQQ6UKatVacS0lNqIvZxzmYS7_NqmVDwdkftctR2D1gTfgss89TPl7oqdFT",
        json=payload,
    )

    if response.ok:
        print("Posted")
    else:
        print("Failed")


def migrate_quest_names_batch():
    users_ref = db.collection("users").where("points", "==", None).stream()

    batch = db.batch()
    operation_count = 0
    updated_count = 0

    for user_doc in users_ref:
        user_data = user_doc.to_dict()
        quests_completed = user_data.get("points")

        if not quests_completed:
            continue

        # Add update to batch
        batch.update(user_doc.reference, {"points": 0})

        operation_count += 1
        updated_count += 1

        # Commit batch when limit reached
        if operation_count >= BATCH_LIMIT:
            batch.commit()
            print(f"✅ Committed {operation_count} updates")

            # Reset batch
            batch = db.batch()
            operation_count = 0

    # Commit any remaining operations
    if operation_count > 0:
        batch.commit()
        print(f"✅ Committed final {operation_count} updates")

    print(f"🎉 Migration complete. Updated {updated_count} users.")


if __name__ == "__main__":
    asyncio.run(post_kofi_summary())
    # asyncio.run(add_killer_card())
    # asyncio.run(generate_test_card())
    # reset_coins()
    # migrate_shop_prices()
    # backfill_wordle_stats()
    # asyncio.run(find_users_with_doom_card())
    # get_all_users()
    # choose_new_word()
    # asyncio.run(
    #    add_item(
    #        "696254108788719627",
    #        "Smoked Card",
    #        "card",
    #        "smoked_card.png",
    #        "custom.png",
    #        "rare",
    #    )
    # )
    # asyncio.run(test_fetch_call())
# asyncio.run(generate_inventory(userId="292040660696039424"))
# asyncio.run(backfill_ccids())
# asyncio.run(generate_wordle_share(None, "292040660696039424"))
