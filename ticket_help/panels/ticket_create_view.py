import discord

from .boss_multiselect_view import BossMultiSelectView
from .server_select import ServerSelect
from .ticket_modal import CreateTicketModal
from .type_select import TypeSelect


class TicketCreateView(discord.ui.View):
    def __init__(self, servers: list[dict]):
        super().__init__(timeout=120)

        self.selected_type = "daily bosses"
        self.selected_server = ""

        self.add_item(TypeSelect())
        self.add_item(ServerSelect(servers))

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=2)
    async def next_step(self, interaction: discord.Interaction, _):

        if not self.selected_server:
            await interaction.response.send_message(
                "❌ Please select a server before continuing.",
                ephemeral=True,
            )
            return

        if self.selected_type in {"other bosses", "spamming", "testing", "until drop"}:
            await interaction.response.send_modal(
                CreateTicketModal(
                    ticket_type=self.selected_type,
                    server=self.selected_server,
                    bosses=[],
                )
            )
            return

        await interaction.response.defer()

        view = BossMultiSelectView(
            ticket_type=self.selected_type, server=self.selected_server
        )

        await interaction.edit_original_response(
            content="Select all bosses for this ticket:", view=view
        )
