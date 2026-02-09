from datetime import datetime

import discord
from commands.permissions import has_admin_role
from dashboard.updater import update_dashboard
from discord import app_commands
from firebase_client import db, firestore
from tickets.embed_utils import build_ticket_embed
from tickets.points import clear_point_rule_cache
from tickets.utils import clear_active_ticket
from tickets.views import TicketActionView


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

    if not doc:
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
                )

                await message.edit(embed=embed, view=view)
            except discord.NotFound:
                pass

    if interaction.channel:
        await interaction.channel.send(
            f"🧹 {user.mention} was removed from ticket **{ticket_name}** by an admin."
        )


@app_commands.command(name="add-points", description="Add points to a user")
async def add_points(
    interaction: discord.Interaction, user: discord.Member, points: int
):

    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    user_doc = db.collection("users").document(str(user.id))
    user_data = user_doc.get().to_dict()

    if not user_data:
        return await interaction.response.send_message(
            f"❌ User `{user.name}` does not exist.", ephemeral=True
        )

    user_doc.update({"points": user_data.get("points", 0) + points})

    await interaction.response.send_message(
        f"✅ Points for user `{user.name}` updated.", ephemeral=True
    )

    await update_dashboard(interaction.client)


@app_commands.command(name="subtract-points", description="Subtract points from a user")
async def subtract_points(
    interaction: discord.Interaction, user: discord.Member, points: int
):

    if not has_admin_role(interaction):
        return await interaction.response.send_message(
            "🚫 You do not have permission to use this command.", ephemeral=True
        )

    user_doc = db.collection("users").document(str(user.id))
    user_data = user_doc.get().to_dict()

    if not user_data:
        return await interaction.response.send_message(
            f"❌ User `{user.name}` does not exist.", ephemeral=True
        )

    user_doc.update({"points": user_data.get("points", 0) - points})

    await interaction.response.send_message(
        f"✅ Points for user `{user.name}` updated.", ephemeral=True
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
