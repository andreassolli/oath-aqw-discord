import random
from typing import List, Literal

from google.cloud import firestore

from economy.utils import ShopItem
from firebase_client import db
from inventory.utils import add_item


async def list_item(
    name: str,
    coin_price: int,
    shard_price: int,
    image: str,
    type: str,
    quantity: int | None = None,
    priority: int | None = None,
    invisible: bool = False,
    rarity: Literal["common", "uncommon", "rare", "epic", "legendary"] = "common",
):
    if quantity is None:
        quantity = -1

    # If no priority provided -> auto assign highest + 1
    if priority is None:
        docs = (
            db.collection("shop_items")
            .order_by("priority", direction="DESCENDING")
            .limit(1)
            .stream()
        )

        highest = 0
        for doc in docs:
            highest = doc.to_dict().get("priority", 0)

        priority = highest + 1

    image_path = f"{image}.png"
    display_path = f"{image}_item.png"

    db.collection("shop_items").document(name).set(
        {
            "name": name,
            "coin_price": coin_price,
            "shard_price": shard_price,
            "quantity": quantity,
            "display": display_path,
            "image": image_path,
            "type": type,
            "priority": priority,
            "invisible": invisible,
            "rarity": rarity,
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
    name = item.get("name")
    docs = db.collection("shop_items").where("name", "==", name).limit(1).get()

    if not docs:
        return "Item not found."

    item_ref = docs[0].reference
    # Already owned
    if any(i.get("id") == name for i in inventory):
        return f"You already own {name}."

    quantity = item.get("quantity", 0)
    coin_price = item.get("coin_price", 0)
    shard_price = item.get("shard_price", 0)

    user_coins = user_data.get("coins", 0)
    user_shards = user_data.get("gems", 0)

    # No stock
    if quantity == 0:
        return f"There are no more {name} available."

    # Not enough coins
    if coin_price > 0 and user_coins < coin_price:
        return f"You do not have enough Coins to buy {name}."

    # Not enough shards
    if shard_price > 0 and user_shards < shard_price:
        return f"You do not have enough Chaos Shards to buy {name}."

    # Deduct currency
    updates = {}

    if coin_price > 0:
        updates["coins"] = firestore.Increment(-coin_price)

    if shard_price > 0:
        updates["gems"] = firestore.Increment(-shard_price)

    if updates:
        user_ref.update(updates)

    await add_item(
        str(user_id),
        name,
        item.get("type", ""),
        item.get("image", ""),
        item.get("display", ""),
    )

    parts = []

    if coin_price > 0:
        parts.append(f"{coin_price} Coins")

    if shard_price > 0:
        parts.append(f"{shard_price} Chaos Shards")

    price_str = " and ".join(parts)
    # Update stock
    if quantity != -1:
        item_ref.update({"quantity": firestore.Increment(-1)})

    return f"Bought 1 of {name} for {price_str}."


async def get_shop() -> List[ShopItem]:
    docs = db.collection("shop_items").stream()

    items: List[ShopItem] = []
    for doc in docs:
        data = doc.to_dict()
        if data:
            items.append(data)  # type: ignore

    return items
