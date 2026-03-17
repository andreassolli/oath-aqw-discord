from typing import List, TypedDict

import discord
from numpy import quantile

from firebase_client import db


class ShopItem(TypedDict):
    name: str
    price: int
    image: str
    display: str
    quantity: int


def rich_coins(guild: discord.Guild):
    users = (
        db.collection("users")
        .order_by("coins", direction="DESCENDING")
        .limit(15)
        .stream()
    )

    medals = ["🥇", "🥈", "🥉"]
    lines = []

    for i, doc in enumerate(users):
        data = doc.to_dict() or {}

        position = i + 1
        member = guild.get_member(int(doc.id))

        display_name = (
            member.display_name if member else data.get("aqw_username", "Unknown User")
        )

        coins = data.get("coins", 0)

        if i < 3:
            prefix = medals[i]
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

    embed = discord.Embed(
        title="<:oathcoin:1462999179998531614> Top 15 Richest",
        description="\n".join(lines),
        color=discord.Color.gold(),
    )

    return embed
