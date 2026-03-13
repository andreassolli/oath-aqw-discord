from typing import Dict, List

import discord

from economy.operations import buy_item
from economy.utils import ShopItem


class ShopSelect(discord.ui.Select):
    def __init__(self, items: List[ShopItem]):
        options = [
            discord.SelectOption(
                label=item["name"],
                description=f"{item['price']} coins",
                value=item["name"],
            )
            for item in items
        ]

        super().__init__(
            placeholder="Select an item to buy",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        view.selected_item = self.values[0]


class BuyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Buy Selected",
            style=discord.ButtonStyle.success,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view

        if not view.selected_item:
            return await interaction.response.send_message(
                "Select an item first.",
                ephemeral=True,
            )

        response = await buy_item(view.selected_item, interaction.user.id)

        await interaction.response.send_message(response, ephemeral=True)


class ShopView(discord.ui.View):
    def __init__(self, items: List[ShopItem]):
        super().__init__(timeout=180)

        self.selected_item: str | None = None

        self.add_item(ShopSelect(items))
        self.add_item(BuyButton())
