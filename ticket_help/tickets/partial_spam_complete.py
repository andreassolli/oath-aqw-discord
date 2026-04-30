import bisect

import discord

from config import spam_points
from firebase_client import db
from ticket_help.tickets.completion_utils import finalize_ticket


class SpamAmountModal(discord.ui.Modal, title="Enter completed runs/kills"):
    amount = discord.ui.TextInput(
        label="Amount",
        placeholder="Enter a number",
        required=True,
    )

    def __init__(
        self,
        ticket_name: str,
        kills: int,
        type: str = "",
    ):
        super().__init__()
        self.ticket_name = ticket_name
        self.kills = kills
        self.type = type

    def build_modified_data(self, original_data, kills):
        completed_points = 0
        if self.type == "Full TempleShrine":
            completed_points = int(kills * 1.75)
        elif self.type == "Middle TempleShrine":
            completed_points = int(kills * 0.75)
        elif self.type == "Side TempleShrine":
            completed_points = int(kills * 0.5)
        else:
            index = bisect.bisect_left(spam_points, kills)
            completed_points = spam_points[index - 1] if index > 0 else 0

        modified_data = original_data.copy()
        modified_data["total_kills"] = kills
        modified_data["points"] = completed_points
        return modified_data

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            amount = int(self.amount.value)
        except ValueError:
            await interaction.response.send_message(
                "❌ Please enter a valid number.",
                ephemeral=True,
            )
            return

        if amount < 1 or amount > self.kills:
            await interaction.response.send_message(
                f"❌ Number must be between 1 and {self.kills}.",
                ephemeral=True,
            )
            return

        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            await interaction.response.send_message(
                "❌ Ticket not found.",
                ephemeral=True,
            )
            return

        data = doc.to_dict()
        modified_data = self.build_modified_data(data, amount)

        modified_data["total_kills"] = amount

        await finalize_ticket(
            interaction=interaction,
            ticket_name=self.ticket_name,
            ticket_data=modified_data,
        )
