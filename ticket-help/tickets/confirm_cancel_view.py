import discord
from firebase_admin import firestore
from tickets.utils import clear_active_ticket
from dashboard.updater import update_dashboard
from commands.permissions import has_admin_role, has_oathsworn_role
from firebase_client import db
from tickets.logging import log_ticket_event
from tickets.embed_logging import build_logging_embed


class ConfirmCancelView(discord.ui.View):
    def __init__(self, ticket_name: str, ticket_data: dict):
        super().__init__(timeout=30)
        self.ticket_name = ticket_name
        self.ticket_data = ticket_data
        self.confirmed = False


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        requester_id = self.ticket_data.get("user_id")

        is_requester = interaction.user.id == requester_id
        is_admin = has_admin_role(interaction)
        is_oathsworn = has_oathsworn_role(interaction)

        if not (is_requester or is_admin or is_oathsworn):
            await interaction.response.send_message(
                "🚫 You can’t interact with this confirmation.",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(label="✅ Yes, cancel ticket", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, _):
        self.confirmed = True

        doc_ref = db.collection("tickets").document(self.ticket_name)

        embed = build_logging_embed(
            requester_id=self.ticket_data["user_id"],
            bosses=self.ticket_data.get("bosses", []),
            username=self.ticket_data.get("username", "—"),
            max_claims=self.ticket_data.get("max_claims", 0),
            claimers=self.ticket_data.get("claimers", []),
            guild=interaction.guild,
            type=self.ticket_data.get("type", "unknown"),
            created_at=self.ticket_data.get("created_at"),
            closer_id=interaction.user.id,
            cancelled=True,
        )
        doc_ref.update({
            "status": "cancelled",
            "closed_by": interaction.user.id,
            "closed_at": firestore.SERVER_TIMESTAMP,
        })

        clear_active_ticket(self.ticket_data["user_id"], self.ticket_name)
        claimers = self.ticket_data.get("claimers", [])
        for user_id in claimers:
            clear_active_ticket(user_id, self.ticket_name)

        await interaction.response.edit_message(
            content="🗑️ Ticket cancelled.",
            view=None
        )

        claimer_mentions = ", ".join(f"<@{uid}>" for uid in claimers) or "None"
        closer_mention = interaction.user.mention
        requester_id = self.ticket_data.get("user_id")
        await log_ticket_event(interaction.client, embed=embed)

        await update_dashboard(interaction.client)
        await interaction.channel.delete()

    @discord.ui.button(label="❌ No, keep ticket", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _):
        await interaction.response.edit_message(
            content="✅ Ticket was **not** cancelled.",
            view=None
        )

    async def on_timeout(self):
        if not self.confirmed:
            for item in self.children:
                item.disabled = True
