import random
from datetime import datetime, timedelta, timezone

import discord
from google.cloud import firestore

from firebase_client import db


def buy_rock_break(user: discord.User, price: int):
    user_ref = db.collection("users").document(str(user.id))
    doc = user_ref.get()

    if not doc.exists:
        coins = 0
    else:
        user_data = doc.to_dict()
        coins = user_data.get("coins", 0)

    if coins >= price:
        user_ref.update(
            {
                "coins": coins - price,
                "transactions": firestore.ArrayUnion([f"- Broke a rock for ${price}"]),
            }
        )
        return True
    return False


async def get_break_cooldown(user_id: int):
    doc = db.collection("users").document(str(user_id)).get()

    if not doc.exists:
        return None

    last_break = doc.to_dict().get("last_break")
    if not last_break:
        return None

    if last_break.tzinfo is None:
        last_break = last_break.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)

    remaining = timedelta(hours=4) - (now - last_break)

    if remaining.total_seconds() <= 0:
        return None

    return remaining


async def set_broken(user_id: int):
    db.collection("users").document(str(user_id)).set(
        {"last_break": datetime.now(timezone.utc)}, merge=True
    )
