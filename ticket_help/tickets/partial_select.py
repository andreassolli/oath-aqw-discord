import discord

from firebase_client import db


def get_points_for_boss(boss: str) -> int:
    for doc in db.collection("point_rules").stream():
        if doc.id.lower() == boss.lower():
            return int(doc.to_dict().get("points", 1))
    return 1


class PartialSelect(discord.ui.Select):
    def __init__(self, ticket_name: str, bosses: list[str], parent_view):
        options = [discord.SelectOption(label=boss, value=boss) for boss in bosses]

        super().__init__(
            placeholder="Select completed bosses...",
            min_values=1,
            max_values=len(options),
            options=options,
        )

        self.ticket_name = ticket_name
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.selected_bosses = self.values

        await interaction.response.edit_message(
            content=f"✅ Selected: {', '.join(self.values)}", view=self.parent_view
        )
