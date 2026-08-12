import discord

from panels.test_boss import BossMultiSelectView
from ticket_help.modals.test_modal import CreateTicketModal
from ticket_help.panels.server_select import ServerSelect
from ticket_help.panels.type_select import PracticeSelect, TypeSelect
from panels.spam_view import SpamCreateView
from panels.spam_cache import SPAM_PANEL_CACHE

class TicketCreateView(discord.ui.View):
    def __init__(self, servers):
        super().__init__(timeout=600)

        self.selected_type = "daily bosses"
        self.selected_practice = "standard"
        self.servers = servers

        self.add_item(TypeSelect())
        self.add_item(PracticeSelect())

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, row=2)
    async def next_step(self, interaction: discord.Interaction, _):
        if self.selected_practice == "infinity" and self.selected_type != "spamming":
            return await interaction.response.send_message(
                "You can only create spamming tickets for AQW:I.", ephemeral=True
            )

        if self.selected_practice != "infinity" and self.selected_type == "spamming":
            await interaction.response.defer(ephemeral=True)

            await interaction.followup.send(
                "Add the bosses you need help with using the command `/add-bosses <boss1> <boss2>`",
                ephemeral=True
            )

            SPAM_PANEL_CACHE[interaction.user.id] = {
                "is_practice": self.selected_practice,
                "type": self.selected_type,
                "servers": self.servers,
                "bosses": [],
            }
            return

        await interaction.response.send_modal(
            CreateTicketModal(
                ticket_type=self.selected_type,
                username=interaction.user.display_name,
                servers=self.servers,
                is_practice=self.selected_practice == "practice",
                is_infinity=self.selected_practice == "infinity",
            )
        )
