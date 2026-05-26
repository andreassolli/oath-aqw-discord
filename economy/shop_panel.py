import math
import traceback

import discord

from economy.operations import buy_item
from economy.utils import ShopItem
from firebase_client import db

RARITY_EMOJIS = {
    "common": "🟢",
    "uncommon": "🔵",
    "rare": "🔴",
    "epic": "🟣",
    "legendary": "🟠",
}


class ShopLayout(discord.ui.LayoutView):
    def __init__(self, shop_items: list[ShopItem], user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        self.enabled_filters = {
            "card",
            "border",
            "claim",
            "item",
        }
        doc = db.collection("users").document(str(user.id)).get()
        data = doc.to_dict() or {}

        self.coins = data.get("coins", 0)
        self.gems = data.get("gems", 0)
        self.all_shop_items = shop_items
        self.shop_items = shop_items
        self.page = 0
        self.per_page = 2

        self.container = self.build_container()
        self.add_item(self.container)

    def get_filtered_items(self):
        return [
            item for item in self.all_shop_items if item["type"] in self.enabled_filters
        ]

    def get_page_items(self):
        filtered = self.get_filtered_items()

        start = self.page * self.per_page
        end = start + self.per_page

        return filtered[start:end]

    def build_container(self):
        total_pages = max(
            1,
            math.ceil(len(self.get_filtered_items()) / self.per_page),
        )

        items: list[discord.ui.Item] = [
            discord.ui.TextDisplay(
                content=f"**Shop** (Page {self.page + 1}/{total_pages})\nYour purse: <:oathcoin:1462999179998531614>{self.coins}, <:gems:1485660490376937502>{self.gems}"
            ),
            discord.ui.Separator(
                visible=False,
                spacing=discord.SeparatorSpacing.small,
            ),
            discord.ui.ActionRow(
                FilterButton(
                    "Cards",
                    "🎨",
                    "card",
                    "card" in self.enabled_filters,
                ),
                FilterButton(
                    "Borders",
                    "🖼️",
                    "border",
                    "border" in self.enabled_filters,
                ),
                FilterButton(
                    "Claims",
                    "🔱",
                    "claim",
                    "claim" in self.enabled_filters,
                ),
                FilterButton(
                    "Items",
                    "🧸",
                    "item",
                    "item" in self.enabled_filters,
                ),
            ),
            discord.ui.Separator(
                visible=False,
                spacing=discord.SeparatorSpacing.small,
            ),
        ]

        for item in self.get_page_items():
            items.append(
                discord.ui.MediaGallery(
                    discord.MediaGalleryItem(
                        media=f"https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/{item['display']}",
                    ),
                ),
            )
            items.append(
                discord.ui.Section(
                    discord.ui.TextDisplay(
                        content=(
                            f"**{item['name']} {item['type'].capitalize()}** (Stock: `{'∞' if item['quantity'] == -1 else item['quantity']}`)\n"
                            f">>> `{RARITY_EMOJIS.get(item.get('rarity', 'common'), '⚪')}` "
                            f"{item.get('rarity', 'common').capitalize()} rarity\n"
                            f"**Price:** <:oathcoin:1462999179998531614>{item['coin_price']} "
                            f", <:gems:1485660490376937502>"
                            f"{item['shard_price']} "
                        )
                    ),
                    accessory=BuyButton(item=item),
                )
            )

            items.append(
                discord.ui.Separator(
                    visible=False,
                    spacing=discord.SeparatorSpacing.small,
                )
            )

        nav = []

        if self.page > 0:
            nav.append(PrevPageButton())

        if self.page < total_pages - 1:
            nav.append(NextPageButton())

        if nav:
            items.append(discord.ui.ActionRow(*nav))

        return discord.ui.Container(
            *items,
            accent_colour=discord.Colour(7344907),
        )

    async def update(self, interaction: discord.Interaction):
        try:
            print("Updating shop...")

            await interaction.response.defer()

            self.container = self.build_container()

            self.clear_items()
            self.add_item(self.container)

            await interaction.edit_original_response(view=self)

            print("Shop updated")

        except Exception:
            print("SHOP UPDATE FAILED")
            traceback.print_exc()


class BuyButton(discord.ui.Button):
    def __init__(self, item: ShopItem):
        super().__init__(
            label="Buy",
            style=discord.ButtonStyle.success,
            emoji="🛒",
        )
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        response = await buy_item(
            self.item,
            interaction.user.id,
        )

        await interaction.response.send_message(
            response,
            ephemeral=True,
        )


class NextPageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Next ▶",
            style=discord.ButtonStyle.primary,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopLayout = self.view
        view.page += 1
        await view.update(interaction)


class PrevPageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="◀ Prev",
            style=discord.ButtonStyle.primary,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopLayout = self.view

        if view.page > 0:
            view.page -= 1

        await view.update(interaction)


class FilterButton(discord.ui.Button):
    def __init__(
        self,
        label: str,
        emoji: str,
        item_type: str,
        enabled: bool,
    ):
        super().__init__(
            label=label,
            emoji=emoji,
            style=(
                discord.ButtonStyle.success if enabled else discord.ButtonStyle.danger
            ),
        )

        self.item_type = item_type

    async def callback(
        self,
        interaction: discord.Interaction,
    ):
        view = self.view

        if not isinstance(view, ShopLayout):
            return

        if self.item_type in view.enabled_filters:
            view.enabled_filters.remove(self.item_type)
        else:
            view.enabled_filters.add(self.item_type)

        # reset to page 1 after filtering
        view.page = 0

        await view.update(interaction)
