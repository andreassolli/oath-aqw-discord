import discord

from inventory.view import InventoryView


class BackgroundSelect(discord.ui.Select):
    def __init__(self, backgrounds: list[str]):
        options = [discord.SelectOption(label=b, value=b) for b in backgrounds]

        super().__init__(
            placeholder="Select a background",
            min_values=0,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view
        view.selected_background = self.values[0] if self.values else None

        await interaction.response.send_message(
            f"Selected background: {view.selected_background}", ephemeral=True
        )
