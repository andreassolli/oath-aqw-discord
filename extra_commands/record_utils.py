import aiohttp
from google.cloud import firestore

from config import DISCORD_MANAGER_ROLE_ID, GUILD_ID, MEE6_API
from firebase_client import db
from user_profile.aqwordle_client import db as aqwordle_db


def get_most_counts():
    return (
        db.collection("users")
        .order_by("counting_score", direction="DESCENDING")
        .limit(25)
        .stream()
    )


def get_most_points():
    return (
        db.collection("users")
        .order_by("total_points", direction="DESCENDING")
        .limit(25)
        .stream()
    )


def get_most_claimed():
    return (
        db.collection("users")
        .order_by("total_claimed", direction="DESCENDING")
        .limit(25)
        .stream()
    )


def get_most_coins():
    return (
        db.collection("users")
        .order_by("coins", direction="DESCENDING")
        .limit(50)
        .stream()
    )


def get_aqwordle():
    return


async def get_highest_level():
    user_map = {
        doc.id: (doc.to_dict() or {}) for doc in db.collection("users").stream()
    }

    user_levels = {}

    async with aiohttp.ClientSession() as session:
        url = f"{MEE6_API}{GUILD_ID}?page=0"

        async with session.get(url) as resp:
            if resp.status != 200:
                return None

            data = await resp.json()
            players = data.get("players", [])

            for player in players[25:]:
                user_id = str(player["id"])

                user_data = user_map.get(user_id, {})

                user_levels[int(user_id)] = {
                    "name": user_data.get("aqw_username", "Unknown User"),
                    "level": player["level"],
                }

    return user_levels


async def build_leaderboard(users_ref, field, guild):
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    position = 0

    is_level_board = field == "level" and isinstance(users_ref, dict)

    iterable = (
        sorted(users_ref.items(), key=lambda x: x[1]["level"], reverse=True)
        if is_level_board
        else users_ref
    )

    for item in iterable:
        if len(lines) >= 25:
            break

        position += 1

        if is_level_board:
            user_id, data = item
            display_name = data.get("name", "Unknown User")
            num = data.get("level", 0)

        else:
            doc = item
            data = doc.to_dict() or {}

            if field == "coins":
                member = guild.get_member(int(doc.id))
                if member and any(
                    role.id == DISCORD_MANAGER_ROLE_ID for role in member.roles
                ):
                    position -= 1
                    continue

            display_name = data.get("aqw_username", "Unknown User")
            num = data.get(field, 0)

        prefix = medals[position - 1] if position <= 3 else f"`{position:02}`"

        icon = ""
        if field == "coins":
            icon = "<:oathcoin:1462999179998531614>"
        elif field == "counting_score":
            icon = "🎲"
        elif field == "level":
            icon = "lvl "

        suffix = ""
        if field == "total_points":
            suffix = " pts"
        elif field == "total_claimed":
            suffix = " tickets"

        lines.append(f"{prefix} **{display_name}** — {icon}`{num}`{suffix}")

    return lines
