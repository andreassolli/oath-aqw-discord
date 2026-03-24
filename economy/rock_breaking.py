import random

import discord

from firebase_client import db


def buy_rock_break(user: discord.User):
    user_ref = db.collection("users").document(str(user.id))
    doc = user_ref.get()

    if not doc.exists:
        coins = 0
    else:
        user_data = doc.to_dict()
        coins = user_data.get("coins", 0)

    if coins >= 425:
        user_ref.update({"coins": coins - 425})
        return True
    return False
