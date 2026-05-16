import discord

from firebase_client import db
from ticket_help.tickets.completion_utils import finalize_ticket


class ConfirmModal(discord.ui.Modal, title="Complete Ticket"):
    def __init__(
        self, ticket_name: str, bosses: list[str], type: str = "weekly bosses"
    ):
        super().__init__()
        self.type = type

        options = []
        for boss in bosses:
            option = discord.CheckboxGroupOption(label=boss, value=boss, default=True)
            options.append(option)

        if type in {"weekly bosses", "daily bosses", "7 man bosses"}:
            self.boss_selection = discord.ui.Label(
                text="Completed bosses:",
                component=discord.ui.CheckboxGroup(
                    options=options,
                    required=True,
                ),
            )
            self.add_item(self.boss_selection)
            self.keep_ticket = discord.ui.Label(
                text="Keep ticket. Select if a helper has to leave",
                component=discord.ui.Checkbox(),
            )
            self.add_item(self.keep_ticket)

        self.ticket_name = ticket_name

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()
        data = doc.to_dict()

        # 🔒 Hard guard
        if data.get("status") in ("completing", "completed"):
            return await interaction.followup.send(
                "⚠️ This ticket has already been completed.", ephemeral=True
            )

        if self.type in {"weekly bosses", "daily bosses", "7 man bosses"}:
            completed_bosses = [
                option.value
                for option in self.boss_selection.component.options
                if option.value in data.get("bosses", [])
            ]
            doc_ref.update({"completed_bosses": completed_bosses})

            await finalize_ticket(
                interaction=interaction,
                ticket_name=self.ticket_name,
                ticket_data=data,
                keep_ticket=self.keep_ticket.component.value,
            )
        else:
            await finalize_ticket(
                interaction=interaction,
                ticket_name=self.ticket_name,
                ticket_data=data,
                keep_ticket=False,
            )
