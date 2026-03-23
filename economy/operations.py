import random
from typing import List, Literal

from google.cloud import firestore

from economy.utils import ShopItem
from firebase_client import db
from inventory.utils import add_item


async def list_item(
    name: str,
    price: int,
    image: str,
    currency: Literal["coins", "gems"],
    type: str,
    quantity: int | None = None,
):
    if quantity == None:
        quantity = -1
    image_path = f"{image}.png"
    display_path = f"{image}_item.png"
    db.collection("shop_items").document(name).set(
        {
            "name": name,
            "price": price,
            "quantity": quantity,
            "display": display_path,
            "image": image_path,
            "currency": currency,
            "type": type,
        }
    )
    return


async def unlist_item(name: str):
    docs = db.collection("shop_items").where("name", "==", name).get()

    if docs:
        docs[0].reference.delete()


async def buy_item(item: ShopItem, user_id: int):
    user_ref = db.collection("users").document(str(user_id))
    user_doc = user_ref.get()
    user_data = user_doc.to_dict() or {}
    inventory = user_data.get("inventory", [])
    item_ref = db.collection("shop_items").document(item.get("name"))
    name = item.get("name")

    # Already owned
    if any(i.get("id") == name for i in inventory):
        return f"You already own {name}."

    quantity = item.get("quantity", 0)
    price = item.get("price", 0)

    currency = item.get("currency", "coins")

    # Normalize currency (IMPORTANT)
    if currency == "gem":
        currency = "gems"

    money = user_data.get(currency, 0)

    if quantity == 0:
        return f"There are no more {name} available."

    if money < price:
        return f"You do not have enough {currency} to buy {name}."

    # Deduct currency
    user_ref.update({currency: firestore.Increment(-price)})

    await add_item(
        str(user_id),
        name,
        item.get("type", ""),
        item.get("image", ""),
        item.get("display", ""),
    )

    # Update stock
    if quantity != -1:
        item_ref.update({"quantity": firestore.Increment(-1)})

    return f"Bought 1 of {name}, you now have {money - price} {currency}."


async def get_shop() -> List[ShopItem]:
    docs = db.collection("shop_items").stream()

    items: List[ShopItem] = []
    for doc in docs:
        data = doc.to_dict()
        if data:
            items.append(data)  # type: ignore

    return items
