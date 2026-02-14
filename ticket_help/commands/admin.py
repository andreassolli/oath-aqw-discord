from datetime import datetime
from typing import List

import discord
from discord import app_commands

from config import ALLOWED_COMMANDS_CHANNELS, TICKET_LOG_CHANNEL_ID
from firebase_client import db, firestore
from ticket_help.commands.permissions import has_admin_role
from ticket_help.dashboard.updater import update_dashboard
from ticket_help.tickets.confirm_cancel_view import ConfirmCancelView
from ticket_help.tickets.confirm_complete_view import ConfirmCompleteView
from ticket_help.tickets.embed_utils import build_ticket_embed
from ticket_help.tickets.points import clear_point_rule_cache
from ticket_help.tickets.utils import clear_active_ticket
from ticket_help.tickets.views import TicketActionView


@app_commands.command(
    name="cancel-ticket", description="Force cancel a ticket with confirmation"
)
async def cancel_ticket_command(
    interaction: discord.Interaction,
    ticket_name: str,
):
    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.",
            ephemeral=True,
        )

    await interaction.response.defer(ephemeral=True)

    doc_ref = db.collection("tickets").document(ticket_name)
    doc = doc_ref.get()

    if not doc.exists:
        return await interaction.followup.send(
            f"❌ Ticket `{ticket_name}` not found.",
            ephemeral=True,
        )

    data = doc.to_dict()

    if data.get("status") in ("completed", "cancelled"):
        return await interaction.followup.send(
            "⚠️ This ticket is already closed.",
            ephemeral=True,
        )

    view = ConfirmCancelView(ticket_name=ticket_name, ticket_data=data)

    await interaction.followup.send(
        f"⚠️ Are you sure you want to cancel ticket **{ticket_name}**?",
        view=view,
        ephemeral=True,
    )


@app_commands.command(
    name="complete-ticket",
    description="Force complete a ticket with confirmation",
)
async def complete_ticket_command(
    interaction: discord.Interaction,
    ticket_name: str,
):
    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.",
            ephemeral=True,
        )

    await interaction.response.defer(ephemeral=True)

    doc_ref = db.collection("tickets").document(ticket_name)
    doc = doc_ref.get()

    if not doc.exists:
        return await interaction.followup.send(
            f"❌ Ticket `{ticket_name}` not found.",
            ephemeral=True,
        )

    data = doc.to_dict()

    if data.get("status") in ("completed", "cancelled"):
        return await interaction.followup.send(
            "⚠️ This ticket is already closed.",
            ephemeral=True,
        )

    view = ConfirmCompleteView(
        ticket_name=ticket_name,
    )

    await interaction.followup.send(
        f"⚠️ Are you sure you want to complete ticket **{ticket_name}**?",
        view=view,
        ephemeral=True,
    )


@app_commands.command(
    name="clear-active-ticket", description="Clear a user's active ticket"
)
async def clear_active_ticket_command(
    interaction: discord.Interaction, user: discord.Member, ticket_name: str
):

    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    clear_active_ticket(user.id, ticket_name)

    await interaction.response.send_message(
        f"🧹 Cleared active ticket for {user.mention} on ticket **{ticket_name}**.",
        ephemeral=True,
    )


@app_commands.command(
    name="remove-claimer", description="Remove a helper from a ticket"
)
async def remove_claimer(
    interaction: discord.Interaction, ticket_name: str, user: discord.Member
):

    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    doc_ref = db.collection("tickets").document(ticket_name)
    doc = doc_ref.get()

    if not doc.exists:
        return await interaction.response.send_message(
            f"❌ Ticket `{ticket_name}` not found.", ephemeral=True
        )

    data = doc.to_dict()
    claimers = data.get("claimers", [])

    if user.id not in claimers:
        return await interaction.response.send_message(
            f"ℹ️ {user.mention} is not a claimer on this ticket.", ephemeral=True
        )

    claimers.remove(user.id)
    doc_ref.update({"claimers": claimers})

    clear_active_ticket(user.id, ticket_name)

    await interaction.response.send_message(
        f"🧹 Removed {user.mention} from ticket **{ticket_name}**.", ephemeral=True
    )

    channel_id = data.get("channel_id")
    message_id = data.get("message_id")

    if channel_id and message_id:
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            try:
                message = await channel.fetch_message(message_id)

                view = TicketActionView(
                    ticket_name=ticket_name,
                    max_claims=data.get("max_claims"),
                    room=data.get("room"),
                    bosses=data.get("bosses"),
                )

                embed = build_ticket_embed(
                    requester_id=data["user_id"],
                    bosses=data["bosses"],
                    points=data["points"],
                    username=data["username"],
                    room=data["room"],
                    max_claims=data["max_claims"],
                    claimers=claimers,
                    guild=interaction.guild,
                    type=data["type"],
                    server=data["server"],
                    total_kills=data["total_kills"],
                )

                await message.edit(embed=embed, view=view)
            except discord.NotFound:
                pass

    if interaction.channel:
        await interaction.channel.send(
            f"🧹 {user.mention} was removed from ticket **{ticket_name}** by an admin."
        )


@app_commands.command(
    name="adjust-points",
    description="Add or subtract points from multiple users or a role",
)
@app_commands.describe(
    users="Mention users separated by spaces",
    role="Apply to entire role instead",
    points="Use positive to add, negative to subtract",
)
async def adjust_points(
    interaction: discord.Interaction,
    points: int,
    users: str | None = None,
    role: discord.Role | None = None,
):
    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission.",
            ephemeral=True,
        )

    if not users and not role:
        return await interaction.response.send_message(
            "❌ Provide either users or a role.",
            ephemeral=True,
        )

    if users and role:
        return await interaction.response.send_message(
            "❌ Choose either users OR a role, not both.",
            ephemeral=True,
        )

    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    if guild is None:
        return await interaction.followup.send(
            "❌ Must be used inside a server.",
            ephemeral=True,
        )

    log_channel = guild.get_channel(TICKET_LOG_CHANNEL_ID)

    # --- Resolve targets ---
    targets: List[discord.Member] = []

    if role:
        targets = role.members

    elif users:
        # Extract IDs from mentions like <@123> or <@!123>
        import re

        ids = re.findall(r"\d{17,20}", users)

        for user_id in ids:
            member = guild.get_member(int(user_id))
            if member:
                targets.append(member)

    if not targets:
        return await interaction.followup.send(
            "❌ No valid users found.",
            ephemeral=True,
        )

    updated_count = 0
    changes = []
    for member in targets:
        user_ref = db.collection("users").document(str(member.id))
        doc = user_ref.get()

        if not doc.exists:
            continue

        data = doc.to_dict() or {}
        before = data.get("points", 0)
        after = max(0, before + points)  # prevent negative

        user_ref.update({"points": after})
        updated_count += 1
        changes.append(f"{member.mention} — {before} → {after} ({points:+})")

    if isinstance(log_channel, discord.TextChannel) and changes:
        embed = discord.Embed(
            title="💰 Bulk Points Adjustment",
            color=discord.Color.green() if points >= 0 else discord.Color.red(),
            timestamp=discord.utils.utcnow(),
        )

        embed.add_field(
            name="Moderator",
            value=interaction.user.mention,
            inline=True,
        )

        embed.add_field(
            name="Amount",
            value=f"{points:+} points",
            inline=True,
        )

        embed.add_field(
            name="Affected Users",
            value="\n".join(changes),
            inline=False,
        )

        await log_channel.send(embed=embed)

    await interaction.followup.send(
        f"✅ Adjusted {updated_count} user(s) by {points:+} points.",
        ephemeral=True,
    )

    await update_dashboard(interaction.client)


@app_commands.command(name="set-boss-points", description="Set the points for a boss")
async def set_boss_points(
    interaction: discord.Interaction, boss_name: str, points: int
):

    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    doc_ref = db.collection("point_rules").document(boss_name)
    doc = doc_ref.get()

    if not doc.exists:
        return await interaction.response.send_message(
            f"❌ Boss `{boss_name}` does not exist.", ephemeral=True
        )

    doc_ref.update({"points": points})

    await interaction.response.send_message(
        f"✅ Points for boss `{boss_name}` set to `{points}`.", ephemeral=True
    )

    await update_dashboard(interaction.client)


@app_commands.command(
    name="toggle-boss-available", description="Toggle boss availability"
)
async def toggle_boss_available(
    interaction: discord.Interaction, type_name: str, boss_name: str
):

    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    doc_ref = db.collection("point_rules").document(type_name)
    doc = doc_ref.get()

    if not doc.exists:
        return await interaction.response.send_message(
            f"❌ Ticket type `{type_name}` does not exist.", ephemeral=True
        )

    bosses = doc.to_dict().get("bosses", [])
    if boss_name in bosses:
        bosses.remove(boss_name)
    else:
        bosses.append(boss_name)

    doc_ref.set({"bosses": bosses})

    await interaction.response.send_message(
        f"Boss **{boss_name}** is now {'available' if boss_name in bosses else 'unavailable'} for type **{type_name}**.",
        ephemeral=True,
    )


@app_commands.command(name="list-bosses", description="List all bosses for type")
async def list_bosses(interaction: discord.Interaction, type_name: str):

    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    doc_ref = db.collection("bosses").document(type_name)
    doc = doc_ref.get()

    if not doc.exists:
        return await interaction.response.send_message(
            f"❌ Ticket type `{type_name}` does not exist.", ephemeral=True
        )

    bosses = doc.to_dict().get("bosses", [])
    await interaction.response.send_message(
        f"Bosses for type **{type_name}**: {', '.join(bosses)}", ephemeral=True
    )


@app_commands.command(name="add-type", description="Add a new ticket type")
async def add_type(
    interaction: discord.Interaction,
    type_name: str,
):

    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    type_name = type_name.lower().strip()

    doc_ref = db.collection("bosses").document(type_name)
    doc = doc_ref.get()

    if doc.exists:
        return await interaction.response.send_message(
            f"❌ Ticket type `{type_name}` already exists.", ephemeral=True
        )

    doc_ref.set({"bosses": []})

    await interaction.response.send_message(
        f"✅ Ticket type **{type_name}** has been created.", ephemeral=True
    )


@app_commands.command(name="delete-type", description="Delete a ticket type")
async def delete_type(interaction: discord.Interaction, type_name: str):

    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    doc_ref = db.collection("bosses").document(type_name)
    doc = doc_ref.get()

    if not doc.exists:
        return await interaction.response.send_message(
            f"❌ Ticket type `{type_name}` does not exist.", ephemeral=True
        )

    doc_ref.delete()

    await interaction.response.send_message(
        f"🗑 Ticket type **{type_name}** has been deleted.", ephemeral=True
    )


@app_commands.command(name="lookup", description="Lookup a user's points")
async def lookup_points(interaction: discord.Interaction, user: discord.Member):
    doc_ref = db.collection("users").document(str(user.id))

    if interaction.channel_id not in ALLOWED_COMMANDS_CHANNELS:
        allowed_mentions = ", ".join(f"<#{cid}>" for cid in ALLOWED_COMMANDS_CHANNELS)

        await interaction.response.send_message(
            f"❌ This command can only be used in {allowed_mentions}.",
            ephemeral=True,
        )
        return

    doc = doc_ref.get()
    if doc.exists:
        points = doc.to_dict().get("points", 0)
        await interaction.response.send_message(
            f"**{user.name}** has **{points}** points.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"**{user.name}** has **0** points.", ephemeral=True
        )


@app_commands.command(name="delete-boss", description="Delete a boss")
async def delete_boss(interaction: discord.Interaction, ticket_type: str, boss: str):
    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    doc_ref = db.collection("bosses").document(ticket_type)

    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({"bosses": firestore.ArrayRemove([boss])})
    else:
        return await interaction.response.send_message(
            f"❌ **{ticket_type}** does not exist.", ephemeral=True
        )

    await interaction.response.send_message(
        f"✅ Removed **{boss}** from **{ticket_type}** bosses.", ephemeral=True
    )


@app_commands.command(
    name="add-boss", description="Add a boss to a ticket type with points"
)
async def add_boss(
    interaction: discord.Interaction,
    ticket_type: str,
    boss: str,
    points: int,
    room: str,
):
    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    # Ticket type → bosses list
    type_ref = db.collection("bosses").document(ticket_type)
    type_doc = type_ref.get()

    if type_doc.exists:
        type_ref.update({"bosses": firestore.ArrayUnion([boss])})
    else:
        type_ref.set({"bosses": [boss]})

    boss_ref = db.collection("point_rules").document(boss)

    boss_ref.set({"points": points, "room": room}, merge=True)

    await interaction.response.send_message(
        f"✅ Added **{boss}** to **{ticket_type}** with **{points}** points in **{room}**.",
        ephemeral=True,
    )


@app_commands.command(
    name="reset-all-points", description="Archive and reset all user points"
)
async def reset_all_points(interaction: discord.Interaction):
    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)

    users_ref = db.collection("users")
    users = list(users_ref.stream())

    if not users:
        return await interaction.followup.send(
            "ℹ️ No users found to reset.", ephemeral=True
        )

    archive_data = {}
    for doc in users:
        data = doc.to_dict()
        archive_data[doc.id] = {
            "points": data.get("points", 0),
            "tickets_claimed": data.get("tickets_claimed", 0),
        }

    archive_id = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

    db.collection("points_archive").document(archive_id).set(
        {
            "created_at": firestore.SERVER_TIMESTAMP,
            "reset_by": interaction.user.id,
            "users": archive_data,
        }
    )

    batch = db.batch()
    for doc in users:
        batch.update(doc.reference, {"points": 0, "tickets_claimed": 0})
    batch.commit()

    await interaction.followup.send(
        f"✅ All user points have been reset.\n📦 Archive ID: `{archive_id}`",
        ephemeral=True,
    )

    await update_dashboard(interaction.client)


@app_commands.command(
    name="set-user-points", description="Manually set a user's points"
)
async def set_user_points(
    interaction: discord.Interaction, user: discord.Member, points: int
):
    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    if points < 0 or points > 1_000_000:
        return await interaction.response.send_message(
            "❌ Invalid points amount.", ephemeral=True
        )

    user_ref = db.collection("users").document(str(user.id))

    user_ref.set({"points": points}, merge=True)

    await interaction.response.send_message(
        f"✅ Set **{user.mention}** points to **{points}**.", ephemeral=True
    )

    await update_dashboard(interaction.client)


@app_commands.command(
    name="reload-point-rules", description="Reload ticket point rules from the database"
)
async def reload_point_rules(interaction: discord.Interaction):
    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    clear_point_rule_cache()

    await interaction.response.send_message(
        "🔄 Point rules cache reloaded from Firestore.", ephemeral=True
    )
