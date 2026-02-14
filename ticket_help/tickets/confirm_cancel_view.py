import discord
from firebase_admin import firestore

from firebase_client import db
from ticket_help.commands.permissions import has_admin_role
from ticket_help.dashboard.updater import update_dashboard

from .embed_logging import build_logging_embed
from .logging import log_ticket_event
from .utils import clear_active_ticket


class ConfirmCancelView(discord.ui.View):
    def __init__(self, ticket_name: str, ticket_data: dict):
        super().__init__(timeout=30)
        self.ticket_name = ticket_name
        self.ticket_data = ticket_data
        self.confirmed = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            await interaction.response.send_message(
                "❌ Ticket data not found.", ephemeral=True
            )
            return False

        data = doc.to_dict()
        requester_id = data["user_id"]

        if interaction.user.id != requester_id and not has_admin_role(interaction):
            await interaction.response.send_message(
                "🚫 You can’t interact with this confirmation.", ephemeral=True
            )
            return False

        return True

    @discord.ui.button(label="✅ Yes, cancel ticket", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, _):
        self.confirmed = True

        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()
        if not doc.exists:
            return await interaction.followup.send(
                "❌ Ticket data not found.", ephemeral=True
            )

        data = doc.to_dict()

        # 🔒 Hard guard (prevent double cancel)
        if data.get("status") in ("cancelled", "completed"):
            return await interaction.followup.send(
                "⚠️ This ticket is already closed.", ephemeral=True
            )

        requester_id = self.ticket_data["user_id"]
        claimers = self.ticket_data.get("claimers", [])
        clear_active_ticket(requester_id, self.ticket_name)
        for user_id in claimers:
            clear_active_ticket(user_id, self.ticket_name)

        requester_member = interaction.guild.get_member(requester_id)
        closer_member = interaction.guild.get_member(interaction.user.id)

        requester_display = (
            requester_member.display_name
            if requester_member
            else f"User {requester_id}"
        )

        closer_display = (
            closer_member.display_name
            if closer_member
            else f"User {interaction.user.id}"
        )

        helper_displays: dict[int, str] = {}

        for user_id in claimers:
            member = interaction.guild.get_member(user_id)
            if member:
                helper_displays[user_id] = member.display_name
            else:
                helper_displays[user_id] = f"User {user_id}"

        embed = build_logging_embed(
            requester_display=requester_display,
            helper_displays=helper_displays,
            closer_display=closer_display,
            requester_before=0,
            requester_after=0,
            helper_changes={},
            requester_id=requester_id,
            bosses=data.get("bosses", []),
            username=data.get("username", "—"),
            max_claims=data.get("max_claims", 0),
            claimers=claimers,
            guild=interaction.guild,
            type=data.get("type", "unknown"),
            created_at=self.ticket_data["created_at"],
            cancelled=True,
            closer_id=interaction.user.id,
        )

        doc_ref.update(
            {
                "status": "cancelled",
                "closed_by": interaction.user.id,
                "closed_at": firestore.SERVER_TIMESTAMP,
            }
        )

        await interaction.response.edit_message(
            content="🗑️ Ticket cancelled.", view=None
        )

        await log_ticket_event(interaction.client, embed=embed)

        await update_dashboard(interaction.client)
        await interaction.channel.delete()

    @discord.ui.button(label="❌ No, keep ticket", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _):
        await interaction.response.edit_message(
            content="✅ Ticket was **not** cancelled.", view=None
        )

    async def on_timeout(self):
        if not self.confirmed:
            for item in self.children:
                item.disabled = True
