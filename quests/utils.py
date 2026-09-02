from datetime import datetime, timezone

from google.cloud import firestore as gc_firestore

from firebase_client import db
from user_profile.utils import fetch_inventory


# ============================================================
# Date / cycle helpers
# ============================================================

def format_date(dt: datetime) -> str:
    return f"{dt.strftime('%B')} {dt.day}, {dt.year}"


def get_weekly_cycle_id() -> str:
    """
    Returns the current weekly quest cycle.

    Example:
        weekly_2026_week_36
    """
    now = datetime.now(timezone.utc)
    iso_year, iso_week, _ = now.isocalendar()

    return f"weekly_{iso_year}_week_{iso_week}"


def get_daily_cycle_id() -> str:
    """
    Returns the current daily cycle.

    Example:
        frequent_2026_09_01
    """
    now = datetime.now(timezone.utc)

    return f"frequent_{now.strftime('%Y_%m_%d')}"


def claim_quest_position(
    user_id: int,
    quest_id: str,
    cycle_id: str,
):
    completion_ref = (
        db.collection("quest-completions")
        .document(
            f"{cycle_id}_{quest_id.replace(' ', '_')}"
        )
    )

    transaction = db.transaction()

    @gc_firestore.transactional
    def transaction_handler(transaction):

        snapshot = completion_ref.get(
            transaction=transaction
        )

        now = datetime.now(timezone.utc)

        if snapshot.exists:
            data = snapshot.to_dict()

            # Existing/legacy quest with ranking disabled.
            if not data.get("ranking_enabled", True):
                return None, 1.0

            # User has already claimed this quest.
            if data.get("first_user") == str(user_id):
                return None, 0.0

            if data.get("second_user") == str(user_id):
                return None, 0.0

            # Second person:
            # 1 base point + 0.5 bonus = 1.5 points
            if not data.get("second_user"):
                transaction.update(
                    completion_ref,
                    {
                        "second_user": str(user_id),
                        "second_completed_at": now,
                    },
                )

                return 2, 1.5

            # Everyone after 1st and 2nd:
            # 1 base point, no bonus
            return None, 1.0

        # First person:
        # 1 base point + 1 bonus = 2 points
        transaction.set(
            completion_ref,
            {
                "quest_id": quest_id,
                "cycle_id": cycle_id,
                "ranking_enabled": True,
                "first_user": str(user_id),
                "first_completed_at": now,
            },
        )

        return 1, 2.0

    return transaction_handler(transaction)

def format_quest_items(required_items: list) -> str:
    names = [
        item["strName"]
        for item in required_items
    ]

    if len(names) == 1:
        return names[0]

    if len(names) == 2:
        return f"{names[0]} and {names[1]}"

    return ", ".join(names[:-1]) + f", and {names[-1]}"


def create_quest_history_entry(
    quest_id: str,
    required_items: list,
    position: int | None,
    points: float,
) -> str:

    now = datetime.now(timezone.utc)

    date_text = format_date(now)
    items_text = format_quest_items(required_items)

    if position == 1:
        placement = "1st (+2 points)"
    elif position == 2:
        placement = "2nd (+1.5 points)"
    else:
        placement = "completed (+1 point)"

    return (
        f"Completed {quest_id} with items {items_text} "
        f"on {date_text} — {placement}"
    )


# ============================================================
# Quest loading
# ============================================================

async def get_weekly_quests() -> dict:
    quests = {}

    for quest_id in [1, 2]:

        items_ref = (
            db.collection("weekly-quests")
            .document(f"quest{quest_id}")
            .collection("items")
            .get()
        )

        items = []

        for doc in items_ref:
            data = doc.to_dict()

            items.append(
                {
                    "strName": data.get("name"),
                    "strType": data.get("type"),
                }
            )

        quests[f"Weekly {quest_id}"] = items

    return quests


async def get_frequent_quests() -> dict:
    quests = {}

    for quest_id in [1, 2]:

        items_ref = (
            db.collection("frequent-quests")
            .document(f"quest{quest_id}")
            .collection("items")
            .get()
        )

        items = []

        for doc in items_ref:
            data = doc.to_dict()

            items.append(
                {
                    "strName": data.get("name"),
                    "strType": data.get("type"),
                }
            )

        quests[f"Frequent {quest_id}"] = items

    return quests


# ============================================================
# Quest completion
# ============================================================

async def check_for_quest_completion(user_id: int) -> str:

    user_ref = (
        db.collection("users")
        .document(str(user_id))
    )

    user_snapshot = user_ref.get()

    if not user_snapshot.exists:
        return "❌ No user found."

    user_dict = user_snapshot.to_dict()

    quests_completed = user_dict.get(
        "quests_completed",
        []
    )

    ccid = user_dict.get("ccid", "")

    if len(quests_completed) >= 4:
        return "✅ You have already completed all quests."

    weekly_quests = await get_weekly_quests()
    frequent_quests = await get_frequent_quests()

    quests = {
        **weekly_quests,
        **frequent_quests,
    }

    inventory = await fetch_inventory(ccid)

    completed_now = []
    completed_text = []
    missing_items = []
    history_entries = []

    coins_to_reward = 0
    quest_points_to_reward = 0.0

    inventory_set = {
        (
            item["strName"],
            item["strType"],
        )
        for item in inventory
    }

    for quest_id, required_items in quests.items():

        if quest_id in quests_completed:
            continue

        if not required_items:
            continue

        # ----------------------------------------------------
        # Check inventory
        # ----------------------------------------------------

        if not items_in_inventory(
            required_items,
            inventory,
        ):

            for item in required_items:

                if (
                    item["strName"],
                    item["strType"],
                ) not in inventory_set:

                    missing_items.append(
                        f"{item['strName']} "
                        f"({item['strType']})"
                    )

            continue

        # ----------------------------------------------------
        # Quest completed
        # ----------------------------------------------------

        completed_now.append(quest_id)

        # Coins are independent from placement.
        if "Frequent" in quest_id:
            coins_to_reward += 150
            cycle_id = get_daily_cycle_id()
        else:
            coins_to_reward += 1000
            cycle_id = get_weekly_cycle_id()

        # ----------------------------------------------------
        # Claim first / second place
        # ----------------------------------------------------

        position, points = claim_quest_position(
            user_id=user_id,
            quest_id=quest_id,
            cycle_id=cycle_id,
        )

        quest_points_to_reward += points

        # ----------------------------------------------------
        # History
        # ----------------------------------------------------

        history_entries.append(
            create_quest_history_entry(
                quest_id=quest_id,
                required_items=required_items,
                position=position,
                points=points,
            )
        )

        # ----------------------------------------------------
        # Discord response
        # ----------------------------------------------------

        if position == 1:
            position_text = " 🥇"
        elif position == 2:
            position_text = " 🥈"
        else:
            position_text = ""

        completed_text.append(
            f"<:queststart:1491012167170920560>"
            f"{quest_id}{position_text}"
        )

    # --------------------------------------------------------
    # Nothing completed
    # --------------------------------------------------------

    if not completed_now:

        return (
            "❌ Missing items to complete quest: "
            + ", ".join(missing_items)
        )

    # --------------------------------------------------------
    # Update user
    # --------------------------------------------------------

    update_data = {
        "quests_completed": gc_firestore.ArrayUnion(
            completed_now
        ),

        "quests_completed_count": gc_firestore.Increment(
            len(completed_now)
        ),

        "quest_points": gc_firestore.Increment(
            quest_points_to_reward
        ),

        "coins": gc_firestore.Increment(
            coins_to_reward
        ),

        "transactions": gc_firestore.ArrayUnion(
            [f"+ Quest reward: ${coins_to_reward}"]
        ),

        "quest_history": gc_firestore.ArrayUnion(
            history_entries
        ),
    }

    user_ref.update(update_data)

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return (
        f"🎉 Completed quests: "
        f"{', '.join(completed_text)}, "
        f"rewarded "
        f"<:oathcoin:1462999179998531614>"
        f"{coins_to_reward} "
        f"and "
        f"{quest_points_to_reward:g} quest points."
    )


# ============================================================
# Inventory helper
# ============================================================

def items_in_inventory(
    required_items: list,
    inventory: list,
) -> bool:

    inventory_set = {
        (
            item["strName"],
            item["strType"],
        )
        for item in inventory
    }

    return all(
        (
            req["strName"],
            req["strType"],
        ) in inventory_set
        for req in required_items
    )
