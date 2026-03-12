import random
from typing import List

from google.cloud import firestore

from economy.utils import ShopItem
from firebase_client import db


async def list_item(name: str, price: int, quantity: int | None = None):
    item_id = random.seed()
    if quantity == None:
        quantity = -1
    db.collection("shop_items").document(str(item_id)).set(
        {"name": name, "price": price, "quantity": quantity}
    )
    return


async def unlist_item(name: str):
    docs = db.collection("shop_items").where("name", "==", name).get()

    if docs:
        docs[0].reference.delete()


async def buy_item(name: str, user_id: int):
    user_ref = db.collection("users").document(str(user_id))
    user_doc = user_ref.get()
    user_data = user_doc.to_dict() or {}

    coins = user_data.get("coins", 0)

    item_docs = db.collection("shop_items").where("name", "==", name).limit(1).get()

    if not item_docs:
        return f"{name} does not exist."

    item_snap = item_docs[0]
    item_doc = item_snap.to_dict() or {}

    quantity = item_doc.get("quantity", 0)
    price = item_doc.get("price", 0)

    if quantity == 0:
        return f"There are no more {name} available."

    if coins < price:
        return f"You do not have enough coins to buy {name}."

    if name == "Test Border":
        user_ref.update({"coins": firestore.Increment(-price), "border": "Test Border"})
    else:
        user_ref.update({"coins": firestore.Increment(-price)})

    if quantity != -1:
        item_snap.reference.update({"quantity": firestore.Increment(-1)})

    return f"Bought 1 of {name}, you now have {coins - price} coins."


async def get_shop() -> List[ShopItem]:
    docs = db.collection("shop_items").stream()

    items: List[ShopItem] = []
    for doc in docs:
        data = doc.to_dict()
        if data:
            items.append(data)  # type: ignore

    return items
