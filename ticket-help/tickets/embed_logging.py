from typing import Optional

import discord
from firebase_client import db


def build_logging_embed(
    *,
    requester_id: int,
    bosses: list[str],
    username: str,
    max_claims: int,
    claimers: list[int],
    guild: discord.Guild,
    type: str,
    created_at: str,
    closer_id: str,
    cancelled: bool,
    points: Optional[int] = None,
):

    requester_member = guild.get_member(requester_id)
    req_ref = db.collection("users").document(str(requester_id))
    req_doc = req_ref.get()
    req_data = req_doc.to_dict() if req_doc.exists else {}
    requester_after = req_data.get("points", 0)
    points_awarded = len(bosses) * 1
    requester_before = requester_after - points_awarded
    requester_mention = (
        requester_member.display_name
        if requester_member
        else req_data.get("username", f"User {requester_id}")
    )

    closer = guild.get_member(closer_id)
    closer_mention = (
        closer.display_name if closer else req_data.get("username", f"User {closer_id}")
    )

    title = "🗑️ Cancelled Ticket" if cancelled else "🎉 Completed Ticket"
    # Resolve claimer mentions
    if claimers:
        helper_lines = []

        for user_id in claimers:
            user_ref = db.collection("users").document(str(user_id))
            user_doc = user_ref.get()
            user_data = user_doc.to_dict() if user_doc.exists else {}
            if points:
                after = user_data.get("points", 0)
                before = after + points

                name = user_data.get("username", f"User {user_id}")

                helper_lines.append(
                    f"**{name}** — {before} → {after} (**+{points}** pts)"
                )
            else:
                name = user_data.get("username", f"User {user_id}")

                helper_lines.append(f"**{name}**")
        helpers_value = "\n".join(helper_lines)
    else:
        helpers_value = "—"

    if cancelled:
        requester_value = f"{requester_mention} — {requester_before} pts"
    else:
        requester_value = (
            f"{requester_mention} — "
            f"{requester_before} → {requester_after} (**+{points_awarded}** pts)"
        )

    embed = discord.Embed(title=title, color=discord.Color.blurple())

    embed.add_field(name="Requester", value=requester_value, inline=True)

    embed.add_field(name="Username", value=username, inline=True)

    embed.add_field(name="Closed by", value=closer_mention, inline=True)

    embed.add_field(name="Bosses", value=", ".join(bosses), inline=False)

    if not cancelled and points is not None:
        embed.add_field(name="Points Awarded", value=str(points), inline=True)

    embed.add_field(name="Type", value=f"{type}", inline=True)

    embed.add_field(name="Helpers", value=helpers_value, inline=False)

    embed.set_footer(text=f"Created: {created_at}")

    return embed
