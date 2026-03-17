import discord

from inventory.utils import equip_item  # adjust import if needed


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
        await interaction.response.defer()


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
        await interaction.response.defer()


class EquipButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Equip Selected",
            style=discord.ButtonStyle.success,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view

        if not view.selected_border and not view.selected_background:
            return await interaction.response.send_message(
                "Select an item first.",
                ephemeral=True,
            )

        responses = []

        # Equip border
        if view.selected_border:
            res = await equip_item(str(view.user_id), view.selected_border)
            if res:
                responses.append(res)

        # Equip background (card)
        if view.selected_background:
            res = await equip_item(str(view.user_id), view.selected_background)
            if res:
                responses.append(res)

        await interaction.response.send_message(
            "\n".join(responses) if responses else "Nothing equipped.",
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
