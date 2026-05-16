import discord

from firebase_client import db


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
        doc_ref.update({"bosses": self.boss_selection.component.values})
        await self.view._update_ticket_embed(interaction)
        await self.layout.refresh(interaction)

        await interaction.response.send_message(
            f"Current bosses: {', '.join(self.boss_selection.component.values)}",
            ephemeral=True,
        )
