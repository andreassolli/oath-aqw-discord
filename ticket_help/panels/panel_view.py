import discord

from .server_fetch import fetch_servers
from .ticket_create_view import TicketCreateView


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.primary)
    async def create_ticket(self, interaction: discord.Interaction, _):

        await interaction.response.defer(ephemeral=True)

        servers = await fetch_servers()

        view = TicketCreateView(servers)

        await interaction.followup.send(
            "Select the type and server for this ticket:",
            view=view,
            ephemeral=True,
        )
