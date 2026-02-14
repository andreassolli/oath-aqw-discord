import discord

from .ticket_create_view import TicketCreateView
from .ticket_modal import CreateTicketModal


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.primary)
    async def create_ticket(self, interaction: discord.Interaction, _):
        await interaction.response.send_message(
            "Select the type and server for this ticket:",
            view=TicketCreateView(),
            ephemeral=True,
        )
