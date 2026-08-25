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
        self.all_shop_items = shop_items
        self.shop_items = shop_items
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
        # Keep titles separate from normal shop inventory.
        self.titles = [
            item
            for item in shop_items
            if item["type"] == "title"
        ]

        self.all_shop_items = [
            item
            for item in shop_items
            if item["type"] != "title"
        ]

        self.shop_items = self.all_shop_items
        self.page = 0
        self.per_page = 3

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
            discord.ui.TextDisplay(content="Buy Display Title"),
            discord.ui.ActionRow(
                TitleSelect(
                    titles=self.titles,
                    selected_title=self.selected_title,
                ),
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

class TitleSelect(discord.ui.Select):
    def __init__(
        self,
        titles: list[ShopItem],
        selected_title: ShopItem | None,
    ):
        options = [
            discord.SelectOption(
                label=title["name"],
                value=str(title["id"]),
                default=(
                    selected_title is not None
                    and selected_title["id"] == title["id"]
                ),
            )
            for title in titles
        ]

        super().__init__(
            placeholder=(
                selected_title["name"]
                if selected_title
                else "Select a title"
            ),
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopLayout = self.view

        selected_id = self.values[0]

        view.selected_title = next(
            (
                title
                for title in view.titles
                if str(title["id"]) == selected_id
            ),
            None,
        )

        await interaction.response.defer()

        view.container = view.build_container()
        view.clear_items()
        view.add_item(view.container)

        await interaction.edit_original_response(view=view)

class BuyTitleButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Buy Title",
            style=discord.ButtonStyle.success,
            emoji="🛒",
        )

    async def callback(self, interaction: discord.Interaction):
        view: ShopLayout = self.view

        if not view.selected_title:
            await interaction.response.send_message(
                "❌ Select a title first.",
                ephemeral=True,
            )
            return

        response = await buy_item(
            view.selected_title,
            interaction.user.id,
        )

        await interaction.response.send_message(
            response,
            ephemeral=True,
        )

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
