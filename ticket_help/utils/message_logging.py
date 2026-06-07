# ticket_help/tickets/logging.py

import discord

from firebase_client import db


def get_ticket_name_from_channel(channel_id: int):
    docs = db.collection("tickets").where("channel_id", "==", channel_id).limit(1).get()

    if not docs:
        return None

    return docs[0].id


async def log_ticket_view_event(
    bot: discord.Client,
    thread_id: int,
    view: discord.ui.LayoutView,
):

    thread = bot.get_channel(thread_id)

    if not thread:
        try:
            thread = await bot.fetch_channel(thread_id)
        except Exception:
            return

    await thread.send(
        view=view,
        allowed_mentions=discord.AllowedMentions.none(),
    )


async def log_ticket_message_event(
    bot: discord.Client,
    thread_id: int,
    author: str,
    content: str,
    event: str,
    files: list[discord.File] | None = None,
):

    thread = bot.get_channel(thread_id)

    if not thread:
        try:
            thread = await bot.fetch_channel(thread_id)
        except Exception:
            return

    color = discord.Color.lighter_gray()
    if event == "boss change":
        color = discord.Color.blue()
    elif event == "complete":
        color = discord.Color.green()
    elif event == "cancel":
        color = discord.Color.red()
    if author == "Oath Bot":
        color = discord.Color.purple()

    embed = discord.Embed(
        title=author,
        description=content,
        color=color,
    )

    if embed:
        await thread.send(
            embed=embed,
            files=files or [],
            allowed_mentions=discord.AllowedMentions.none(),
        )
    else:
        await thread.send(
            content,
            files=files or [],
            allowed_mentions=discord.AllowedMentions.none(),
        )
