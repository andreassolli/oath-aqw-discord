import discord

from panels.test_boss import BossMultiSelectView
from ticket_help.modals.test_modal import CreateTicketModal
from ticket_help.panels.server_select import ServerSelect
from ticket_help.panels.type_select import PracticeSelect, TypeSelect


class TicketCreateView(discord.ui.View):
    def __init__(self, servers):
        super().__init__(timeout=120)

        self.selected_type = "daily bosses"
        self.selected_practice = "standard"
        self.servers = servers

        self.add_item(TypeSelect())
        self.add_item(PracticeSelect())

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=2)
    async def next_step(self, interaction: discord.Interaction, _):
        await interaction.response.send_modal(
            CreateTicketModal(
                ticket_type=self.selected_type,
                username=interaction.user.display_name,
                servers=self.servers,
                is_practice=self.selected_practice == "practice",
            )
        )
