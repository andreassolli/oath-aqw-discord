import discord

class ServerSelect(discord.ui.Select):
    def __init__(self):
        options_array = ["Artix", "Test", "Yorumi", "Safiria", "Swordhaven", "Yokai", "Alteon", "Sepulchure", "Espada", "Galanoth", "Gravelyn"]
        options = [discord.SelectOption(label=option, value=option.lower()) for option in options_array]

        super().__init__(
            placeholder="Artix",
            min_values=1,
            max_values=1,
            options=options,
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_server = self.values[0]
        await interaction.response.defer()
