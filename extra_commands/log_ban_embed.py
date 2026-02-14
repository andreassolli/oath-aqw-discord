import discord


def build_ban_log_embed(
    *,
    guild: discord.Guild,
    target_id: str,
    moderator_id: int,
    reason: str | None,
    action: str,  # "ban" or "unban"
):
    moderator_member = guild.get_member(moderator_id)

    target_display = f"{target_id}"

    moderator_display = (
        moderator_member.display_name if moderator_member else f"{moderator_id}"
    )

    is_ban = action.lower() == "ban"

    embed = discord.Embed(
        title="🚫 User Banned" if is_ban else "✅ User Unbanned",
        color=discord.Color.red() if is_ban else discord.Color.green(),
        timestamp=discord.utils.utcnow(),
    )

    embed.add_field(name="User", value=target_display, inline=True)
    embed.add_field(name="Moderator", value=moderator_display, inline=True)

    if is_ban and reason:
        embed.add_field(name="Reason", value=reason, inline=False)

    embed.set_footer(text=f"User ID: {target_id}")

    return embed
