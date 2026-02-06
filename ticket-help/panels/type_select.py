import discord
from tickets.types import get_type_choices

class TypeSelect(discord.ui.Select):
    def __init__(self):
        options = []

        for type in get_type_choices():
            options.append(
                discord.SelectOption(
                    label=type["id"].title(),
                    value=type["id"],
                )
            )

        super().__init__(
            placeholder="Daily Bosses",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):

        self.view.selected_type = self.values[0]
        await interaction.response.defer()
