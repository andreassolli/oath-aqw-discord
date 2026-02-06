from datetime import datetime, timedelta
from typing import Optional

import discord
from firebase_admin import firestore
from firebase_client import db


def get_week_start(dt: datetime):
    # Monday start (ISO week)
    return dt - timedelta(days=dt.weekday())


def set_active_ticket(user_id: int, ticket_name: str):
    user_ref = db.collection("users").document(str(user_id))
    user_ref.set({"active_ticket": ticket_name}, merge=True)


def clear_active_ticket(user_id: int, ticket_name: Optional[str] = None):

    user_ref = db.collection("users").document(str(user_id))
    doc = user_ref.get()

    if not doc.exists:
        return

    data = doc.to_dict() or {}

    if ticket_name is None or data.get("active_ticket") == ticket_name:
        user_ref.update({"active_ticket": firestore.DELETE_FIELD})


async def find_guide_threads(
    guild: discord.Guild,
    guide_channel_id: int,
    bosses: list[str],
) -> dict[str, discord.Thread]:
    """
    Returns {boss_name: thread} for matched guide threads.
    """
    channel = guild.get_channel(guide_channel_id)
    if not channel:
        return {}

    matches: dict[str, discord.Thread] = {}
    bosses_lower = [b.lower() for b in bosses]

    # Active threads
    threads = list(channel.threads)

    # Archived threads (important!)
    async for thread in channel.archived_threads(limit=100):
        threads.append(thread)

    for thread in threads:
        title = thread.name.lower()
        for boss, boss_l in zip(bosses, bosses_lower):
            if boss_l in title and boss not in matches:
                matches[boss] = thread

    return matches
