import discord

class BossMultiSelect(discord.ui.Select):
    def __init__(self, bosses: list[str]):
        options = [
            discord.SelectOption(label=boss, value=boss)
            for boss in bosses
        ]

        super().__init__(
            placeholder="Select one or more bosses",
            min_values=1,
            max_values=len(options),
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_bosses = self.values
        await interaction.response.defer()
