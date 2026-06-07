# ticket_help/tickets/logging.py

import discord

from firebase_client import db


def get_ticket_name_from_channel(channel_id: int):
    docs = db.collection("tickets").where("channel_id", "==", channel_id).limit(1).get()

    if not docs:
        return None

    return docs[0].id


async def log_ticket_message_event(
    bot: discord.Client,
    ticket_name: str,
    content: str,
    files: list[discord.File] | None = None,
):
    doc = db.collection("tickets").document(ticket_name).get()

    if not doc.exists:
        return

    data = doc.to_dict()

    thread_id = data.get("thread_id")
    if not thread_id:
        return

    thread = bot.get_channel(thread_id)

    if not thread:
        try:
            thread = await bot.fetch_channel(thread_id)
        except Exception:
            return

    await thread.send(
        content,
        files=files or [],
        allowed_mentions=discord.AllowedMentions.none(),
    )
