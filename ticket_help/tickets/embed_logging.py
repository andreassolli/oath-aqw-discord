from typing import Optional

import discord


def build_logging_embed(
    *,
    requester_id: int,
    requester_display: str,
    bosses: list[str],
    username: str,
    max_claims: int,
    claimers: list[int],
    helper_displays: dict[int, str],
    guild: discord.Guild,
    type: str,
    created_at: str,
    closer_id: int,
    closer_display: str,
    cancelled: bool,
    points: Optional[int] = None,
    total_kills: Optional[str] = None,
    requester_before: int,
    requester_after: int,
    helper_changes: dict[int, tuple[int, int]],
    id: int,
) -> discord.Embed:
    """
    Pure embed builder.
    No database reads.
    No mutations.
    Only formats provided data.
    """

    title = f"🗑️ Cancelled Ticket {id}" if cancelled else f"🎉 Completed Ticket {id}"
    embed = discord.Embed(
        title=title,
        color=discord.Color.red() if cancelled else discord.Color.blurple(),
    )

    # ---- Requester ----
    if cancelled:
        requester_value = requester_display
    else:
        points_awarded = requester_after - requester_before
        requester_value = (
            f"{requester_display} — "
            f"{requester_before} → {requester_after} "
            f"(**+{points_awarded}** pts)"
        )

    embed.add_field(name="Requester", value=requester_value, inline=True)
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Closed by", value=closer_display, inline=True)

    # ---- Bosses ----
    embed.add_field(
        name="Bosses",
        value=", ".join(bosses) if bosses else "—",
        inline=False,
    )

    # ---- Extra Fields ----
    if type == "spamming" and total_kills:
        embed.add_field(name="Total Kills", value=total_kills, inline=True)

    if not cancelled and points is not None:
        embed.add_field(name="Base Points", value=str(points), inline=True)

    embed.add_field(name="Type", value=type, inline=True)

    # ---- Helpers ----
    if claimers:
        helper_lines = []

        for user_id in claimers:
            display = helper_displays.get(user_id, f"User {user_id}")
            before, after = helper_changes.get(user_id, (0, 0))
            points_added = after - before

            if cancelled:
                helper_lines.append(f"**{display}**")
            else:
                helper_lines.append(
                    f"**{display}** — {before} → {after} (**+{points_added}** pts)"
                )

        helpers_value = "\n".join(helper_lines)
    else:
        helpers_value = "—"

    embed.add_field(name="Helpers", value=helpers_value, inline=False)

    embed.set_footer(text=f"Created: {created_at}")

    return embed
