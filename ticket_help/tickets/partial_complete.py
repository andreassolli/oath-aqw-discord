import discord

from firebase_client import db
from ticket_help.tickets.completion_utils import finalize_ticket
from ticket_help.tickets.partial_select import PartialSelect


def get_points_for_boss(boss: str) -> int:
    for doc in db.collection("point_rules").stream():
        if doc.id.lower() == boss.lower():
            return int(doc.to_dict().get("points", 1))
    return 1


class PartialCompleteView(discord.ui.View):
    def __init__(self, ticket_name: str, bosses: list[str]):
        super().__init__(timeout=120)

        self.ticket_name = ticket_name
        self.bosses = bosses
        self.selected_bosses = []

        self.select = PartialSelect(ticket_name, bosses, parent_view=self)
        self.add_item(self.select)

    def build_modified_data(self, original_data):
        completed = self.selected_bosses
        all_bosses = self.bosses

        completed_points = sum(get_points_for_boss(b) for b in completed)

        formatted_bosses = []
        for boss in all_bosses:
            if boss in completed:
                formatted_bosses.append(boss)
            else:
                formatted_bosses.append(f"~~{boss}~~")

        modified_data = original_data.copy()
        modified_data["bosses"] = formatted_bosses
        modified_data["points"] = completed_points
        modified_data["completed_bosses"] = completed

        return modified_data

    @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, _):
        await interaction.response.defer(ephemeral=True)

        if not self.selected_bosses:
            return await interaction.followup.send(
                "❌ You must select at least one boss.", ephemeral=True
            )

        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.followup.send(
                "❌ Ticket not found.", ephemeral=True
            )

        data = doc.to_dict()
        modified_data = self.build_modified_data(data)

        await finalize_ticket(
            interaction=interaction,
            ticket_name=self.ticket_name,
            ticket_data=modified_data,
        )

    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(
            "❌ Partial completion cancelled.", ephemeral=True
        )
