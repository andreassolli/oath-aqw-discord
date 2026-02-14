import discord

from .utils import get_badge_category


def build_badge_log_embed(
    *,
    guild: discord.Guild,
    discord_id: int,
    passed: list[str],
    failed: list[str],
    category_counts: dict[str, int],
):
    member = guild.get_member(discord_id)

    display = member.display_name if member else f"User {discord_id}"

    embed = discord.Embed(
        title="🎖️ Badge Application Processed",
        color=discord.Color.blurple(),
        timestamp=discord.utils.utcnow(),
    )

    embed.add_field(name="User", value=display, inline=True)

    def format_badge(badge: str) -> str:
        category = get_badge_category(badge)
        if category and category in category_counts:
            count = category_counts[category]
            return f"• {badge}  *(Current: {count})*"
        return f"• {badge}"

    if passed:
        embed.add_field(
            name="✅ Granted / Upgraded",
            value="\n".join(format_badge(b) for b in passed),
            inline=False,
        )

    if failed:
        embed.add_field(
            name="❌ Failed",
            value="\n".join(format_badge(b) for b in failed),
            inline=False,
        )

    embed.set_footer(text=f"Discord ID: {discord_id}")

    return embed
