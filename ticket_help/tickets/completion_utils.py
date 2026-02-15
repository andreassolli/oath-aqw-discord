from datetime import datetime
from typing import Dict, Tuple

import discord
from firebase_admin import firestore

from config import WEEKLY_REQUESTER_CAP
from firebase_client import db
from ticket_help.dashboard.updater import update_dashboard

from .embed_logging import build_logging_embed
from .logging import log_ticket_event
from .utils import clear_active_ticket, get_week_start


async def finalize_ticket(
    *,
    interaction: discord.Interaction,
    ticket_name: str,
    ticket_data: dict,
) -> None:

    guild = interaction.guild
    if guild is None:
        return

    doc_ref = db.collection("tickets").document(ticket_name)

    requester_id = ticket_data["user_id"]
    points = ticket_data.get("points", 1)

    # 🔒 Lock ticket immediately
    doc_ref.update(
        {
            "status": "completing",
            "closed_by": interaction.user.id,
            "closed_at": firestore.SERVER_TIMESTAMP,
        }
    )

    claimers = [uid for uid in ticket_data.get("claimers", []) if uid != requester_id]

    helper_changes: Dict[int, Tuple[int, int]] = {}
    helper_displays: Dict[int, str] = {}

    for user_id in claimers:
        user_ref = db.collection("users").document(str(user_id))
        helper_doc = user_ref.get()

        before = helper_doc.to_dict().get("points", 0) if helper_doc.exists else 0
        after = before + points

        helper_changes[user_id] = (before, after)

        member = guild.get_member(user_id)
        display = member.display_name if member else f"User {user_id}"
        helper_displays[user_id] = display

        clear_active_ticket(user_id, ticket_name)

        if helper_doc.exists:
            user_ref.update(
                {
                    "username": display,
                    "points": firestore.Increment(points),
                    "tickets_claimed": firestore.Increment(1),
                }
            )
        else:
            user_ref.set(
                {
                    "username": display,
                    "points": points,
                    "tickets_claimed": 1,
                }
            )

    requester_ref = db.collection("users").document(str(requester_id))
    requester_doc = requester_ref.get()

    amount_bosses = len(ticket_data.get("bosses", []))
    ticket_type = ticket_data.get("type")

    MULTIPLIERS = {
        "testing": 0,
        "7 man bosses": 1,
    }

    multiplier = MULTIPLIERS.get(ticket_type, 1)

    if ticket_type == "spamming":
        reward = points // 2
        reward = max(reward, 1)
    else:
        reward = multiplier * amount_bosses

    now = datetime.utcnow()
    week_start = get_week_start(now)

    weekly_points = 0
    weekly_reset = None
    requester_before = 0

    if requester_doc.exists:
        user_data = requester_doc.to_dict()
        weekly_points = user_data.get("weekly_points", 0)
        weekly_reset = user_data.get("weekly_points_reset")
        requester_before = user_data.get("points", 0)

    if not weekly_reset or weekly_reset.replace(tzinfo=None) < week_start:
        weekly_points = 0
        weekly_reset = week_start

    remaining = max(0, WEEKLY_REQUESTER_CAP - weekly_points)
    final_reward = min(reward, remaining)

    updates = {
        "weekly_points": weekly_points + final_reward,
        "weekly_points_reset": weekly_reset,
    }

    if final_reward > 0:
        updates["points"] = firestore.Increment(final_reward)

    if requester_doc.exists:
        requester_ref.update(updates)
    else:
        updates["points"] = final_reward
        updates["tickets_claimed"] = 1
        requester_ref.set(updates)

    clear_active_ticket(requester_id, ticket_name)

    requester_after = requester_before + final_reward

    requester_member = guild.get_member(requester_id)
    requester_display = (
        requester_member.display_name if requester_member else f"User {requester_id}"
    )

    closer_member = guild.get_member(interaction.user.id)
    closer_display = (
        closer_member.display_name if closer_member else f"User {interaction.user.id}"
    )

    embed = build_logging_embed(
        requester_id=requester_id,
        requester_display=requester_display,
        bosses=ticket_data.get("bosses", []),
        username=ticket_data.get("username", "—"),
        max_claims=ticket_data.get("max_claims", 0),
        claimers=claimers,
        helper_displays=helper_displays,
        guild=guild,
        type=ticket_data.get("type", "unknown"),
        created_at=ticket_data.get("created_at"),
        closer_id=interaction.user.id,
        closer_display=closer_display,
        cancelled=False,
        points=points,
        total_kills=ticket_data.get("total_kills"),
        requester_before=requester_before,
        requester_after=requester_after,
        helper_changes=helper_changes,
        id=ticket_data.get("ticket_id", 0),
    )

    doc_ref.update({"status": "completed"})

    await log_ticket_event(interaction.client, embed=embed)
    await update_dashboard(interaction.client)

    await interaction.followup.send("🎉 Ticket completed.", ephemeral=True)

    if interaction.channel:
        await interaction.channel.delete()
