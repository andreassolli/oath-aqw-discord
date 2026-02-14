from datetime import datetime
from typing import Any, Dict, List

import discord


def build_ban_list_embed(bans: List[Dict[str, Any]]) -> discord.Embed:
    embed = discord.Embed(
        title="🚫 Banned Users",
        color=discord.Color.red(),
    )

    if not bans:
        embed.description = "No users are currently banned."
        return embed

    lines = []

    for entry in bans:
        discord_id = entry.get("discord_id")
        username = entry.get("username", "Unknown")
        reason = entry.get("reason", "No reason provided")
        banned_at = entry.get("banned_at")

        # Format Firestore timestamp safely
        if banned_at and hasattr(banned_at, "strftime"):
            date_str = banned_at.strftime("%Y-%m-%d")
        else:
            date_str = "Unknown date"

        lines.append(
            f"**{username}** (`{discord_id}`) *at {date_str}*\n• Reason: {reason}\n"
        )

    # Discord embed description limit = 4096 chars
    description = "\n".join(lines)

    if len(description) > 4000:
        description = description[:3900] + "\n\n⚠️ Too many bans to display."

    embed.description = description
    embed.set_footer(text=f"Total banned users: {len(bans)}")

    return embed
