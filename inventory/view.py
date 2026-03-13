import discord

from firebase_client import db


class BorderSelect(discord.ui.Select):
    def __init__(self, borders: list[str]):
        options = [discord.SelectOption(label=b, value=b) for b in borders]

        super().__init__(
            placeholder="Select a border",
            min_values=0,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        view.selected_border = self.values[0] if self.values else None


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
        view = self.view
        view.selected_background = self.values[0] if self.values else None


class EquipButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Equip Selected",
            style=discord.ButtonStyle.success,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view

        user_ref = db.collection("users").document(str(view.user_id))

        updates = {}

        if view.selected_border:
            updates["border"] = view.selected_border

        if view.selected_background:
            updates["background"] = view.selected_background

        if not updates:
            return await interaction.response.send_message(
                "Select an item first.",
                ephemeral=True,
            )

        user_ref.update(updates)

        await interaction.response.send_message(
            "Items equipped successfully!",
            ephemeral=True,
        )


class InventoryView(discord.ui.View):
    def __init__(self, user_id: int, borders: list[str], backgrounds: list[str]):
        super().__init__(timeout=120)

        self.user_id = user_id
        self.selected_border: str | None = None
        self.selected_background: str | None = None

        if borders:
            self.add_item(BorderSelect(borders))

        if backgrounds:
            self.add_item(BackgroundSelect(backgrounds))

        self.add_item(EquipButton())
