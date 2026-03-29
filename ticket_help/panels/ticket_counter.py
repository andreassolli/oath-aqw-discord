from datetime import datetime

import discord

from firebase_client import db


async def build_ticket_counter():
    ticket_stats_ref = db.collection("meta").document("ticket_stats").get()
    ticket_stats_doc = ticket_stats_ref.to_dict() or {}

    total_completed = ticket_stats_doc.get("total_completed", 0)
    total_points = ticket_stats_doc.get("total_points", 0)

    embed = discord.Embed(
        title="Ticket stats since January 26th, 2026",
        description=(
            f"🎫 `{total_completed}` tickets completed.\n"
            f"🏅 `{total_points}` points given out."
        ),
        color=discord.Color.dark_gold(),
        timestamp=datetime.utcnow(),
    )

    embed.set_footer(
        text="A huge thank you to each and every one of you who made this possible!❤️"
    )

    return embed
