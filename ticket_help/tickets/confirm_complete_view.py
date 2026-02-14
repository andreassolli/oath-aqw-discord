from datetime import datetime

import discord
from firebase_admin import firestore

from config import WEEKLY_REQUESTER_CAP
from firebase_client import db
from ticket_help.commands.permissions import has_admin_role
from ticket_help.dashboard.updater import update_dashboard

from .completion_utils import finalize_ticket
from .embed_logging import build_logging_embed
from .logging import log_ticket_event
from .utils import clear_active_ticket, get_week_start


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

    @discord.ui.button(
        label="✅ Yes, confirm ticket", style=discord.ButtonStyle.success
    )
    async def confirm(self, interaction: discord.Interaction, _):
        self.confirmed = True
        await interaction.response.defer(ephemeral=True)

        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        guild = interaction.guild
        if guild is None:
            return await interaction.followup.send(
                "❌ This interaction is not in a guild.", ephemeral=True
            )

        if not doc.exists:
            return await interaction.followup.send(
                "❌ Ticket data not found.", ephemeral=True
            )

        data = doc.to_dict()

        # 🔒 Hard guard
        if data.get("status") in ("completing", "completed"):
            return await interaction.followup.send(
                "⚠️ This ticket has already been completed.", ephemeral=True
            )

        await finalize_ticket(
            interaction=interaction,
            ticket_name=self.ticket_name,
            ticket_data=data,
        )

    @discord.ui.button(label="❌ No, keep ticket", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _):
        self.confirmed = True
        await interaction.message.edit(
            content="✅ Ticket was **not** completed.", view=None
        )

    async def on_timeout(self):
        if not self.confirmed:
            for item in self.children:
                item.disabled = True
