import discord

from firebase_client import db
from ticket_help.tickets.points import calculate_ticket_points


class ChangeBossModal(discord.ui.Modal, title="Change Bosses"):
    def __init__(
        self, layout, ticket_name: str, bosses: dict[str, str], current: list[str]
    ):
        super().__init__()
        self.layout = layout
        self.ticket_name = ticket_name
        options = []
        for boss in bosses:
            option = discord.CheckboxGroupOption(
                label=boss.get("name"),
                value=boss.get("name"),
                default=boss.get("name") in current,
            )
            options.append(option)

        self.boss_selection = discord.ui.Label(
            text="Select the bosses for this ticket",
            component=discord.ui.CheckboxGroup(
                options=options,
                required=True,
            ),
        )
        self.add_item(self.boss_selection)
        self.ticket_name = ticket_name

    async def on_submit(self, interaction: discord.Interaction):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        points = 0
        for boss in self.boss_selection.component.values:
            points += calculate_ticket_points(boss)

        doc_ref.update(
            {
                "bosses": self.boss_selection.component.values,
                "points": points,
            }
        )

        await interaction.response.send_message(
            f"Current bosses: {', '.join(self.boss_selection.component.values)}, points: {points}",
            ephemeral=True,
        )
