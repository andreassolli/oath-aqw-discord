import math
from typing import Dict, List

import discord

from economy.helpers import filter_items, paginate_items
from economy.operations import buy_item
from economy.shop_generation import generate_shop
from economy.utils import ShopItem

RARITY_EMOJIS = {
    "common": "🟢",
    "uncommon": "🔵",
    "rare": "🔴",
    "epic": "🟣",
    "legendary": "🟠",
}


class RaritySelect(discord.ui.Select):
    def __init__(self, rarities: list[str]):
        options = [
            discord.SelectOption(
                label=f"{RARITY_EMOJIS.get(r, '🟢')} {r.capitalize()}", value=r
            )
            for r in rarities
        ]

        super().__init__(
            placeholder="Filter by rarity",
            min_values=0,  # allow clearing filter
            max_values=len(options),  # multi-select
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopView = self.view
        view.selected_rarities = set(self.values) if self.values else None
        view.page = 0  # reset page when filtering
        await view.update(interaction)


class ShopSelect(discord.ui.Select):
    def __init__(self, items: List[ShopItem]):
        options = [
            discord.SelectOption(
                label=item["name"],
                description=(
                    f"{item['coin_price']} Coins"
                    if item["coin_price"] > 0 and item["shard_price"] == 0
                    else f"{item['shard_price']} Shards"
                    if item["coin_price"] == 0 and item["shard_price"] > 0
                    else f"{item['coin_price']} Coins, {item['shard_price']} Shards"
                ),
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
        selected_name = self.values[0]

        # Find full item object
        item = next((i for i in view.current_items if i["name"] == selected_name), None)

        view.selected_item = item

        await interaction.response.defer()


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


class NextPageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Next ▶", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view: ShopView = self.view
        view.page += 1
        await view.update(interaction)


class PrevPageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="◀ Prev", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        view: ShopView = self.view
        if view.page > 0:
            view.page -= 1
        await view.update(interaction)


class ShopView(discord.ui.View):
    def __init__(self, user_id: int, items: List[ShopItem]):
        super().__init__(timeout=180)

        self.user_id = user_id
        self.all_items = items
        self.page = 0
        self.min_price = None
        self.max_price = None
        self.selected_item: ShopItem | None = None
        self.selected_rarities: set[str] | None = None
        initial_items = paginate_items(items, 0, 8)
        self.current_items = initial_items
        self.select = ShopSelect(initial_items)
        self.add_item(self.select)
        all_rarities = sorted({item.get("rarity", "common") for item in items})

        self.add_item(RaritySelect(all_rarities))
        self.add_item(BuyButton())
        self.add_item(PrevPageButton())
        self.add_item(NextPageButton())

    async def update(self, interaction: discord.Interaction):

        filtered = filter_items(self.all_items, self.min_price, self.max_price)

        if self.selected_rarities:
            filtered = [
                item
                for item in filtered
                if item.get("rarity", "common") in self.selected_rarities
            ]
        total_pages = max(1, math.ceil(len(filtered) / 8))

        # Clamp page
        if self.page >= total_pages:
            self.page = total_pages - 1

        page_items = paginate_items(filtered, self.page, 8)
        self.current_items = page_items
        if not page_items and self.page > 0:
            self.page -= 1
            page_items = paginate_items(filtered, self.page, 8)

        # Update dropdown
        # Rebuild UI (THIS is where selection persistence happens)
        self.clear_items()

        # --- Rarity Select (with defaults) ---
        all_rarities = sorted({item.get("rarity", "common") for item in self.all_items})
        rarity_select = RaritySelect(all_rarities)

        if self.selected_rarities:
            for option in rarity_select.options:
                if option.value in self.selected_rarities:
                    option.default = True

        self.add_item(rarity_select)

        # --- Item Select ---
        self.select = ShopSelect(page_items)
        self.add_item(self.select)

        # --- Buttons ---
        self.add_item(BuyButton())
        self.add_item(PrevPageButton())
        self.add_item(NextPageButton())

        # Generate image
        buffer = await generate_shop(
            items=page_items,
            userId=str(self.user_id),
            page=self.page,
            total_pages=total_pages,
        )

        file = discord.File(buffer, filename="shop.png")

        await interaction.response.edit_message(
            attachments=[file],
            view=self,
        )
