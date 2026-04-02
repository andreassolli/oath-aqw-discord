from google.cloud.firestore import ArrayUnion

from firebase_client import db


async def get_inventory(user_id: str):
    doc_ref = db.collection("users").document(user_id).get()
    doc_data = doc_ref.to_dict() if doc_ref else {}
    inventory = doc_data.get("inventory", {})
    return inventory


async def add_item(
    user_id: str, item_id: str, type: str, image: str, display: str, rarity: str
):
    doc_ref = db.collection("users").document(user_id)
    item = {
        "id": item_id,
        "type": type,
        "image": image,
        "display": display,
        "rarity": rarity,
    }

    doc_ref.update({"inventory": ArrayUnion([item])})


async def equip_item(user_id: str, item_id: str):
    doc_ref = db.collection("users").document(user_id)

    doc = doc_ref.get()
    if not doc:
        return

    data = doc.to_dict() or {}
    inventory = data.get("inventory", [])

    item = next((i for i in inventory if i["id"] == item_id), None)

    if not item:
        return "Item not found in inventory."

    item_type = item["type"]

    doc_ref.update(
        {item_type: {"id": item_id, "image": item["image"], "display": item["display"]}}
    )

    return f"Equipped {item['id']}."


async def unequip_item(user_id: str, type: str):
    doc_ref = db.collection("users").document(user_id)

    doc = doc_ref.get()
    if not doc:
        return

    doc_ref.update({type: None})

    return f"{type} unequipped."
