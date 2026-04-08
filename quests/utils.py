from dataclasses import MISSING

from google.cloud import firestore as gc_firestore

from firebase_client import db
from user_profile.utils import fetch_inventory


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


async def check_for_quest_completion(user_id: int) -> str:
    user_ref = db.collection("users").document(str(user_id))
    user_data = user_ref.get()

    if not user_data.exists:
        return "❌ No user found."

    user_dict = user_data.to_dict()
    quests_completed = user_dict.get("quests_completed", [])
    ccid = user_dict.get("ccid", "")

    if len(quests_completed) >= 4:
        return "✅ You have already completed all quests."

    weekly_quests = await get_weekly_quests()
    frequent_quests = await get_frequent_quests()
    quests = {**weekly_quests, **frequent_quests}
    completed_now = []
    inventory = await fetch_inventory(ccid)
    coins_to_reward = 0
    completed_text = []
    missing_items = []
    inventory_set = {(i["strName"], i["strType"]) for i in inventory}
    for quest_id, required_items in quests.items():
        if quest_id in quests_completed or not required_items:
            continue

        if items_in_inventory(required_items, inventory):
            completed_now.append(quest_id)
            if "Frequent" in quest_id:
                coins_to_reward += 150
            else:
                coins_to_reward += 1000
            completed_text.append(f"<:queststart:1491012167170920560>{quest_id}")
            continue

        for item in required_items:
            if (item["strName"], item["strType"]) not in inventory_set:
                missing_items.append(f"{item['strName']} ({item['strType']})")

    if not completed_now:
        return "❌ Missing items to complete quest: " + ", ".join(missing_items)

    updated_quests = quests_completed + completed_now

    user_ref.update(
        {
            "quests_completed": updated_quests,
            "coins": gc_firestore.Increment(coins_to_reward),
        }
    )

    return f"🎉 Completed quests: {', '.join(completed_text)}, rewarded <:oathcoin:1462999179998531614>{coins_to_reward}."


def items_in_inventory(required_items: list, inventory: list) -> bool:
    inventory_set = {(item["strName"], item["strType"]) for item in inventory}

    return all(
        (req["strName"], req["strType"]) in inventory_set for req in required_items
    )
