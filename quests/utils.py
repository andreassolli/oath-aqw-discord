from cogs.extra import gc_firestore
from firebase_client import db
from user_profile.utils import fetch_inventory


async def get_quests() -> dict:
    quest_refs = {
        "quest_1": db.collection("weekly-quests").document("quest1"),
        "quest_2": db.collection("weekly-quests").document("quest2"),
    }

    quests = {}
    for quest_id, ref in quest_refs.items():
        doc = ref.get()
        if doc.exists:
            quests[quest_id] = doc.to_dict().get("items", [])

    return quests


async def check_for_quest_completion(user_id: int) -> str:
    user_ref = db.collection("users").document(str(user_id))
    user_data = user_ref.get()

    if not user_data.exists:
        return "❌ No user found."

    user_dict = user_data.to_dict()
    quests_completed = user_dict.get("quests_completed", [])
    ccid = user_dict.get("ccid", "")

    if len(quests_completed) >= 2:
        return "✅ You have already completed both quests."

    quests = await get_quests()
    completed_now = []
    inventory = await fetch_inventory(ccid)
    coins_to_reward = 0

    for quest_id, required_items in quests.items():
        if quest_id in quests_completed:
            continue

        if items_in_inventory(required_items, inventory):
            completed_now.append(quest_id)
            coins_to_reward += 1000

    if not completed_now:
        return "❌ No quests completed yet."

    updated_quests = quests_completed + completed_now
    await user_ref.update(
        {
            "quests_completed": updated_quests,
            "coins": gc_firestore.Increment(coins_to_reward),
        }
    )

    return f"🎉 Completed quests: {', '.join(completed_now)}, rewarded {coins_to_reward} coins."


def items_in_inventory(required_items: list, inventory: list) -> bool:
    inventory_set = {(item["strName"], item["strType"]) for item in inventory}

    return all(
        (req["strName"], req["strType"]) in inventory_set for req in required_items
    )
