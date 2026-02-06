import discord
from firebase_admin import firestore
from datetime import datetime
from firebase_client import db
from tickets.utils import clear_active_ticket, get_week_start
from dashboard.updater import update_dashboard
from tickets.logging import log_ticket_event
from tickets.embed_logging import build_logging_embed
from commands.permissions import has_admin_role
from config import WEEKLY_REQUESTER_CAP


class ConfirmCompleteView(discord.ui.View):
    def __init__(self, ticket_name: str):
        super().__init__(timeout=30)
        self.ticket_name = ticket_name
        self.confirmed = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            await interaction.response.send_message(
                "❌ Ticket data not found.",
                ephemeral=True
            )
            return False

        data = doc.to_dict()
        requester_id = data["user_id"]

        if interaction.user.id != requester_id and not has_admin_role(interaction):
            await interaction.response.send_message(
                "🚫 You can’t interact with this confirmation.",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(label="✅ Yes, confirm ticket", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, _):
        self.confirmed = True
        await interaction.response.defer(ephemeral=True)

        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.followup.send(
                "❌ Ticket data not found.",
                ephemeral=True
            )

        data = doc.to_dict()

        # 🔒 Hard guard
        if data.get("status") in ("completing", "completed"):
            return await interaction.followup.send(
                "⚠️ This ticket has already been completed.",
                ephemeral=True
            )

        requester_id = data["user_id"]

        # 🔐 Lock immediately
        doc_ref.update({
            "status": "completing",
            "closed_by": interaction.user.id,
            "closed_at": firestore.SERVER_TIMESTAMP,
        })

        # ---- Award helper points ----
        points = data.get("points", 1)
        claimers = [uid for uid in data.get("claimers", []) if uid != requester_id]

        for user_id in claimers:
            user_ref = db.collection("users").document(str(user_id))
            clear_active_ticket(user_id, self.ticket_name)

            try:
                member = await interaction.guild.fetch_member(user_id)
                username = member.display_name
            except discord.NotFound:
                username = "Unknown"

            if user_ref.get().exists:
                user_ref.update({
                    "username": username,
                    "points": firestore.Increment(points),
                    "tickets_claimed": firestore.Increment(1),
                })
            else:
                user_ref.set({
                    "username": username,
                    "points": points,
                    "tickets_claimed": 1
                })

        # ---- Award requester points ----
        user_ref = db.collection("users").document(str(requester_id))
        user_doc = user_ref.get()

        amount_bosses = len(data.get("bosses", []))
        ticket_type = data.get("type")

        MULTIPLIERS = {
            "testing": 0,
            "spamming": 2,
            "7 man bosses": 2,
        }

        multiplier = MULTIPLIERS.get(ticket_type, 1)
        reward = multiplier * amount_bosses

        now = datetime.utcnow()
        week_start = get_week_start(now)

        weekly_points = 0
        weekly_reset = None

        if user_doc.exists:
            user_data = user_doc.to_dict()
            weekly_points = user_data.get("weekly_points", 0)
            weekly_reset = user_data.get("weekly_points_reset")

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

        if user_doc.exists:
            user_ref.update(updates)
        else:
            updates["points"] = final_reward
            updates["tickets_claimed"] = 1
            user_ref.set(updates)

        clear_active_ticket(requester_id, self.ticket_name)

        embed = build_logging_embed(
            requester_id=requester_id,
            bosses=data.get("bosses", []),
            username=data.get("username", "—"),
            max_claims=data.get("max_claims", 0),
            claimers=claimers,
            guild=interaction.guild,
            type=data.get("type", "unknown"),
            created_at=data.get("created_at"),
            closer_id=interaction.user.id,
            cancelled=False,
            points=points,
        )

        doc_ref.update({"status": "completed"})

        await log_ticket_event(interaction.client, embed=embed)
        await update_dashboard(interaction.client)
        await interaction.followup.send("🎉 Ticket completed.", ephemeral=True)
        await interaction.channel.delete()

    @discord.ui.button(label="❌ No, keep ticket", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _):
        self.confirmed = True
        await interaction.message.edit(
            content="✅ Ticket was **not** completed.",
            view=None
        )

    async def on_timeout(self):
        if not self.confirmed:
            for item in self.children:
                item.disabled = True
