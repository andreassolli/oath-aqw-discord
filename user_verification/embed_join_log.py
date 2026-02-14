from typing import Optional

import discord


def build_join_log_embed(
    *,
    guild: discord.Guild,
    discord_id: int,
    ign: str,
    handled_by_id: int,
    status: str,  # "approved" or "declined"
):
    target_member = guild.get_member(discord_id)
    handler_member = guild.get_member(handled_by_id)

    target_display = (
        target_member.display_name if target_member else f"User {discord_id}"
    )

    handler_display = (
        handler_member.display_name if handler_member else f"User {handled_by_id}"
    )

    if status == "approved":
        title = "✅ Guild Join Approved"
        color = discord.Color.green()
    else:
        title = "❌ Guild Join Declined"
        color = discord.Color.red()

    embed = discord.Embed(
        title=title,
        color=color,
        timestamp=discord.utils.utcnow(),
    )

    embed.add_field(name="User", value=target_display, inline=True)
    embed.add_field(name="IGN", value=ign, inline=True)
    embed.add_field(name="Handled by", value=handler_display, inline=True)

    embed.set_footer(text=f"Discord ID: {discord_id}")

    return embed
