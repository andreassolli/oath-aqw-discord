import discord

from firebase_client import db
from inventory.view import InventoryView


class EquipButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Equip Selected", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view

        user_ref = db.collection("users").document(str(view.user_id))

        updates = {}

        if view.selected_border:
            updates["border"] = view.selected_border

        if view.selected_background:
            updates["background"] = view.selected_background

        if not updates:
            return await interaction.response.send_message(
                "Select an item first.", ephemeral=True
            )

        user_ref.update(updates)

        await interaction.response.send_message(
            "Items equipped successfully!", ephemeral=True
        )
