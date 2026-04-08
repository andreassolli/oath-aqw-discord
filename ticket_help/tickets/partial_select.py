import discord

from firebase_client import db
from ticket_help.tickets.completion_utils import finalize_ticket


def get_points_for_boss(boss: str) -> int:
    for doc in db.collection("point_rules").stream():
        if doc.id.lower() == boss.lower():
            return int(doc.to_dict().get("points", 1))
    return 1


class PartialSelect(discord.ui.Select):
    def __init__(self, ticket_name: str, bosses: list[str]):
        options = [discord.SelectOption(label=boss, value=boss) for boss in bosses]

        super().__init__(
            placeholder="Select completed bosses...",
            min_values=1,
            max_values=len(options),
            options=options,
        )

        self.ticket_name = ticket_name
        self.all_bosses = bosses

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()

        if not doc.exists:
            return await interaction.followup.send(
                "❌ Ticket not found.", ephemeral=True
            )

        data = doc.to_dict()
        selected = self.values
        all_bosses = self.all_bosses

        completed = selected
        not_completed = [b for b in all_bosses if b not in completed]

        completed_points = sum(get_points_for_boss(b) for b in completed)
        total_points = data.get("points", 1)

        formatted_bosses = []
        for boss in all_bosses:
            if boss in completed:
                formatted_bosses.append(boss)
            else:
                formatted_bosses.append(f"~~{boss}~~")

        modified_data = data.copy()

        modified_data["bosses"] = formatted_bosses
        modified_data["points"] = completed_points
        modified_data["completed_bosses"] = completed

        await finalize_ticket(
            interaction=interaction,
            ticket_name=self.ticket_name,
            ticket_data=modified_data,
        )
