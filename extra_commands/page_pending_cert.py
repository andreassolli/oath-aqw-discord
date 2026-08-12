import discord

class PendingApplicationsView(discord.ui.View):
    def __init__(self, pages: list[str]):
        super().__init__(timeout=120)

        self.pages = pages
        self.current_page = 0

        self.previous_button.disabled = True

        if len(self.pages) <= 1:
            self.next_button.disabled = True

    def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= len(self.pages) - 1

    @discord.ui.button(
        label="Previous",
        style=discord.ButtonStyle.secondary,
        emoji="◀️",
    )
    async def previous_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        self.current_page -= 1
        self.update_buttons()

        await interaction.response.edit_message(
            content=self.pages[self.current_page],
            view=self,
        )

    @discord.ui.button(
        label="Next",
        style=discord.ButtonStyle.secondary,
        emoji="▶️",
    )
    async def next_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        self.current_page += 1
        self.update_buttons()

        await interaction.response.edit_message(
            content=self.pages[self.current_page],
            view=self,
        )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
