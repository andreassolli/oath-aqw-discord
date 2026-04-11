import discord

from config import EXPERIENCED_HELPER_ROLE_ID, HELPER_ROLE_ID
from firebase_client import db
from ticket_help.commands.permissions import (
    has_oathsworn_role,
)


class SpecialBossButton(discord.ui.Button):
    def __init__(self, ticket_name: str, parent_view, experienced_only: bool = False):
        label = "🔒 Certified Only" if experienced_only else "🔑 All Helpers"

        super().__init__(
            label=label,
            style=discord.ButtonStyle.danger
            if experienced_only
            else discord.ButtonStyle.success,
            row=2,
        )

        self.ticket_name = ticket_name
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.response.send_message(
                "❌ Ticket not found.",
                ephemeral=True,
            )

        data = doc.to_dict()
        requester_id = data.get("user_id")

        is_requester = interaction.user.id == requester_id
        is_oathsworn = has_oathsworn_role(interaction)

        if not (is_requester or is_oathsworn):
            return await interaction.response.send_message(
                "🚫 Only requester or Admin can toggle this.",
                ephemeral=True,
            )

        current = data.get("experienced_only", False)
        new_value = not current

        doc_ref.update({"experienced_only": new_value})

        self.label = "🔒 Certified Only" if new_value else "🔑 All Helpers"
        self.style = (
            discord.ButtonStyle.danger if new_value else discord.ButtonStyle.success
        )
        view = self.view

        await self.parent_view._update_ticket_embed(interaction)

        status = "🔒 Certified Helpers ONLY" if new_value else "🔑 All Helpers"

        await interaction.followup.send(
            f"👊 Claim mode set to: **{status}**",
            ephemeral=True,
        )
