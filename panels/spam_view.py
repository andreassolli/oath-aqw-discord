import discord

from ticket_help.modals.test_modal import CreateTicketModal

class SpamCreateView(discord.ui.View):
    def __init__(self, servers, type, practice, bosses=None):
        super().__init__(timeout=None)

        self.selected_type = type
        self.selected_practice = practice
        self.servers = servers
        self.bosses = bosses or []

    @discord.ui.button(
        label="Next",
        style=discord.ButtonStyle.primary,
        row=2
    )
    async def next_step(
        self,
        interaction: discord.Interaction,
        _
    ):
        await interaction.response.send_modal(
            CreateTicketModal(
                ticket_type=self.selected_type,
                username=interaction.user.display_name,
                servers=self.servers,
                is_practice=self.selected_practice == "practice",
                is_infinity=self.selected_practice == "infinity",
                spam_bosses=self.bosses,
            )
        )
