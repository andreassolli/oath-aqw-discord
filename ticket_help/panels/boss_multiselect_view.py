import discord

from ticket_help.tickets.boss_type import get_bosses_for_type

from .boss_multiselect import BossMultiSelect
from .ticket_modal import CreateTicketModal


class BossMultiSelectView(discord.ui.View):
    def __init__(self, ticket_type: str, server: str):
        super().__init__(timeout=60)
        self.ticket_type = ticket_type
        self.server = server
        self.selected_bosses = []

        bosses = get_bosses_for_type(ticket_type)

        if not bosses:
            raise ValueError(f"No bosses configured for type '{ticket_type}'")

        self.add_item(BossMultiSelect(bosses))

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=1)
    async def next_step(self, interaction: discord.Interaction, _):
        if not self.selected_bosses:
            return await interaction.response.send_message(
                "❌ Please select at least one boss.", ephemeral=True
            )

        await interaction.response.send_modal(
            CreateTicketModal(
                ticket_type=self.ticket_type,
                server=self.server,
                bosses=self.selected_bosses,
            )
        )
