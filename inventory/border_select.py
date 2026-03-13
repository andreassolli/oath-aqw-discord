import discord

from inventory.view import InventoryView


class BorderSelect(discord.ui.Select):
    def __init__(self, borders: list[str]):
        options = [discord.SelectOption(label=b, value=b) for b in borders]

        super().__init__(
            placeholder="Select a border", min_values=0, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view
        view.selected_border = self.values[0] if self.values else None

        await interaction.response.send_message(
            f"Selected border: {view.selected_border}", ephemeral=True
        )
