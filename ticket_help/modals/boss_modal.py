import discord

from firebase_client import db
from ticket_help.modals.utils import build_ticket_layout


class ChangeBossModal(discord.ui.Modal, title="Change Bosses"):
    def __init__(
        self, ticket_name: str, bosses: dict[str, str], current: dict[str, str]
    ):
        super().__init__()

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

    async def _update_ticket_embed(self, interaction: discord.Interaction):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()
        if not doc.exists:
            return

        ticket_data = doc.to_dict()
        message_id = ticket_data.get("message_id")
        if not message_id:
            return

        try:
            message = await interaction.channel.fetch_message(message_id)
            layout = build_ticket_layout(
                ticket_data,
                interaction.guild,
            )

            await message.edit(view=layout)

        except discord.NotFound:
            pass

    async def on_submit(self, interaction: discord.Interaction):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc_ref.update({"bosses": self.boss_selection.component.values})
        await self._update_ticket_embed(interaction)
        await interaction.response.send_message(
            f"Current bosses: {', '.join(self.boss_selection.component.values)}",
            ephemeral=True,
        )
