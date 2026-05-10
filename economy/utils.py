from typing import List, TypedDict

import discord
from google.cloud import firestore

from config import DISCORD_MANAGER_ROLE_ID
from firebase_client import db


@firestore.transactional
def donate_tx(transaction, sender_ref, receiver_ref, amount):
    sender_doc = sender_ref.get(transaction=transaction)
    data = sender_doc.to_dict() or {}

    coins = data.get("coins", 0)
    locked = data.get("locked_coins", 0)

    if coins - locked < amount:
        raise ValueError("Not enough available coins")

    transaction.update(
        sender_ref,
        {
            "coins": firestore.Increment(-amount),
            "transactions": firestore.ArrayUnion([f"- Donated ${amount}"]),
        },
    )

    transaction.update(
        receiver_ref,
        {
            "coins": firestore.Increment(amount),
            "transactions": firestore.ArrayUnion([f"+ Received ${amount}"]),
        },
    )


class ShopItem(TypedDict):
    name: str
    shard_price: int
    coin_price: int
    image: str
    display: str
    quantity: int


def format_txt(t: str):
    if t.startswith("+"):
        t = t.replace("+", "<:greenUp:1475306546018648290>", 1)
    elif t.startswith("-"):
        t = t.replace("-", "<:redDown:1475306580814598185>", 1)

    return t.replace("$", "<:oathcoin:1462999179998531614>")


def rich_coins(guild: discord.Guild):

    users = (
        db.collection("users")
        .order_by("coins", direction="DESCENDING")
        .limit(50)
        .stream()
    )

    medals = ["🥇", "🥈", "🥉"]
    lines = []
    position = 0

    for doc in users:
        if len(lines) >= 15:
            break

        data = doc.to_dict() or {}
        member = guild.get_member(int(doc.id))

        # ❌ Skip if user has manager role
        if member and any(role.id == DISCORD_MANAGER_ROLE_ID for role in member.roles):
            continue

        position += 1

        display_name = (
            member.display_name if member else data.get("aqw_username", "Unknown User")
        )

        coins = data.get("coins", 0)

        if position <= 3:
            prefix = medals[position - 1]
        else:
            prefix = f"`{position:02}`"

        lines.append(
            f"{prefix} **{display_name}** — <:oathcoin:1462999179998531614>`{coins}`"
        )

    if not lines:
        return discord.Embed(
            title="<:oathcoin:1462999179998531614> Top 15 Richest",
            description="No ticket data yet.",
            color=discord.Color.gold(),
        )

    return discord.Embed(
        title="<:oathcoin:1462999179998531614> Top 15 Richest",
        description="\n".join(lines),
        color=discord.Color.gold(),
    )
