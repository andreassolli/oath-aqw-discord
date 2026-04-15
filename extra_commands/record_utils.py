from google.cloud import firestore

from firebase_client import db


async def get_most_counts():
    return (
        db.collection("users")
        .order_by("counting_score", direction="DESCENDING")
        .limit(25)
        .stream()
    )


async def get_most_points():
    return (
        db.collection("users")
        .order_by("total_points", direction="DESCENDING")
        .limit(25)
        .stream()
    )


async def get_most_claimed():
    return (
        db.collection("users")
        .order_by("total_claimed", direction="DESCENDING")
        .limit(25)
        .stream()
    )


async def get_most_coins():
    return (
        db.collection("users")
        .order_by("coins", direction="DESCENDING")
        .limit(25)
        .stream()
    )


async def build_leaderboard(users_ref, field):
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    position = 0

    async for doc in users_ref:
        if len(lines) >= 15:
            break

        position += 1
        data = doc.to_dict()

        display_name = data.get("aqw_username", "Unknown User")

        num = data.get(field, 0)

        if position <= 3:
            prefix = medals[position - 1]
        else:
            prefix = f"`{position:02}`"

        icon = ""
        if field == "coins":
            icon = "<:oathcoin:1462999179998531614>"

        lines.append(f"{prefix} **{display_name}** — {icon}`{num}`")
    return lines
