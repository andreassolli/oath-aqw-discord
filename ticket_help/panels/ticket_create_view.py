import discord

from .boss_multiselect_view import BossMultiSelectView
from .server_select import ServerSelect
from .ticket_modal import CreateTicketModal
from .type_select import TypeSelect


class TicketCreateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.selected_type = "daily bosses"
        self.selected_server = "artix"

        self.add_item(TypeSelect())
        self.add_item(ServerSelect())

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=2)
    async def next_step(self, interaction: discord.Interaction, _):
        if self.selected_type in {"other bosses", "spamming", "testing"}:
            await interaction.response.send_modal(
                CreateTicketModal(
                    ticket_type=self.selected_type,
                    server=self.selected_server,
                    bosses=[],
                )
            )
            return

        view = BossMultiSelectView(
            ticket_type=self.selected_type, server=self.selected_server
        )

        await interaction.response.edit_message(
            content="Select all bosses for this ticket:", view=view
        )
