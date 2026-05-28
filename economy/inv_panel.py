import math
import traceback

import discord

from economy.utils import ShopItem
from firebase_client import db
from inventory.utils import equip_item, unequip_item

RARITY_EMOJIS = {
    "common": "🟢",
    "uncommon": "🔵",
    "rare": "🔴",
    "epic": "🟣",
    "legendary": "🟠",
}


class InventoryLayout(discord.ui.LayoutView):
    def __init__(self, user: discord.User):
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
        inventory = data.get("inventory", [])

        self.coins = data.get("coins", 0)
        self.gems = data.get("gems", 0)
        equipped_card = data.get("card", None)
        equipped_border = data.get("border", None)
        equipped_claim = data.get("claim", None)
        self.equipped_card = equipped_card
        self.equipped_border = equipped_border
        self.equipped_claim = equipped_claim

        inventory.reverse()
        self.all_items = inventory
        self.current_items = inventory
        self.page = 0
        self.per_page = 3

        self.container = self.build_container()
        self.add_item(self.container)

    def get_filtered_items(self):
        return [item for item in self.all_items if item["type"] in self.enabled_filters]

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
                content=f"**Inventory** (Page {self.page + 1}/{total_pages})\nYour purse: <:oathcoin:1462999179998531614>{self.coins}, <:gems:1485660490376937502>{self.gems}"
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
                            f"**{item['id']} {item['type'].capitalize()}**\n"
                            f">>> `{RARITY_EMOJIS.get(item.get('rarity', 'common'), '⚪')}` "
                            f"{item.get('rarity', 'common').capitalize()} rarity\n"
                        )
                    ),
                    accessory=EquipButton(
                        item=item,
                        equipped=self.is_equipped(item),
                    ),
                )
            )

            items.append(
                discord.ui.Separator(
                    visible=False,
                    spacing=discord.SeparatorSpacing.small,
                )
            )

        nav = []

        prev_disabled = self.page == 0
        nav.append(PrevPageButton(disabled=prev_disabled))

        next_disabled = self.page == total_pages - 1
        nav.append(NextPageButton(disabled=next_disabled))

        if nav:
            items.append(discord.ui.ActionRow(*nav))

        return discord.ui.Container(
            *items,
            accent_colour=discord.Colour(7344907),
        )

    def is_equipped(self, item):
        item_type = item["type"]

        equipped_map = {
            "card": self.equipped_card,
            "border": self.equipped_border,
            "claim": self.equipped_claim,
        }

        equipped = equipped_map.get(item_type)

        if not equipped:
            return False

        return equipped.get("id") == item["id"]

    async def update(self, interaction: discord.Interaction):
        try:
            print("Updating inventory...")

            await interaction.response.defer()

            self.container = self.build_container()

            self.clear_items()
            self.add_item(self.container)

            await interaction.edit_original_response(view=self)

            print("Inventory updated")

        except Exception:
            print("INVENTORY UPDATE FAILED")
            traceback.print_exc()


class EquipButton(discord.ui.Button):
    def __init__(
        self,
        item: ShopItem,
        equipped: bool = False,
    ):
        super().__init__(
            label=("Unequip" if equipped else "Equip"),
            style=(
                discord.ButtonStyle.primary if equipped else discord.ButtonStyle.success
            ),
            emoji=("❌" if equipped else "✨"),
        )

        self.item = item
        self.equipped = equipped

    async def callback(
        self,
        interaction: discord.Interaction,
    ):
        view: InventoryLayout = self.view
        if self.equipped:
            response = await unequip_item(
                str(interaction.user.id),
                self.item["type"],
            )
        else:
            response = await equip_item(
                self.item,
                str(interaction.user.id),
            )

        await interaction.response.send_message(
            response,
            ephemeral=True,
        )
        await view.update(interaction)


class NextPageButton(discord.ui.Button):
    def __init__(self, disabled: bool = False):
        super().__init__(
            label="Next ▶",
            style=discord.ButtonStyle.primary,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryLayout = self.view
        view.page += 1
        await view.update(interaction)


class PrevPageButton(discord.ui.Button):
    def __init__(self, disabled: bool = False):
        super().__init__(
            label="◀ Prev",
            style=discord.ButtonStyle.primary,
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction):
        view: InventoryLayout = self.view

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

        if not isinstance(view, InventoryLayout):
            return

        if self.item_type in view.enabled_filters:
            view.enabled_filters.remove(self.item_type)
        else:
            view.enabled_filters.add(self.item_type)

        # reset to page 1 after filtering
        view.page = 0

        await view.update(interaction)
