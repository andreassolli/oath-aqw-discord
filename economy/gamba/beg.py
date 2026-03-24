import asyncio
from datetime import datetime, timedelta

import discord
from google.cloud import firestore

from economy.gamba.beg_view import BegView
from firebase_client import db


async def beg(user: discord.Member):

    user_ref = db.collection("users").document(str(user.id))
    doc = user_ref.get()
    data = doc.to_dict() if doc.exists else {}

    last_beg = data.get("last_beg")
    coins = data.get("coins", 0)

    # if coins > 100:
    #    return None, "💰 You are too rich to be begging."

    if last_beg:
        last_beg = last_beg.replace(tzinfo=None)
        remaining = timedelta(minutes=20) - (datetime.utcnow() - last_beg)

        if remaining.total_seconds() > 0:
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            return None, f"⏳ You can beg again in {mins}m {secs}s."

    user_ref.set(
        {"last_beg": firestore.SERVER_TIMESTAMP},
        merge=True,
    )

    name = user.display_name

    embed = discord.Embed(
        title=f"{name} is begging for coins...",
        description="Click the button below to donate <:oathcoin:1462999179998531614>1 out of sympathy.",
        color=discord.Color.gold(),
    )

    view = BegView(user)

    return embed, view
