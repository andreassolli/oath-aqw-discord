import math

import discord

from economy.helpers import paginate_items
from economy.inventory import generate_inventory
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


class NextPageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Next ▶", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view
        view.page += 1
        await view.update(interaction)


class PrevPageButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="◀ Prev", style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction):
        view: InventoryView = self.view
        if view.page > 0:
            view.page -= 1
        await view.update(interaction)


class InventoryView(discord.ui.View):
    def __init__(self, user_id: int, items: list):
        super().__init__(timeout=120)

        self.user_id = user_id
        self.all_items = items
        self.page = 0

        self.selected_border: str | None = None
        self.selected_background: str | None = None

        self.per_page = 8

        page_items = paginate_items(items, 0, self.per_page)
        self.current_items = page_items

        self._build_selects(page_items)

        self.add_item(EquipButton())
        self.add_item(PrevPageButton())
        self.add_item(NextPageButton())

    def _build_selects(self, items):
        borders = ["None"]
        backgrounds = ["None"]

        for item in items:
            if item.get("type") == "border":
                borders.append(item["id"])
            if item.get("type") == "card":
                backgrounds.append(item["id"])

        if borders:
            self.add_item(BorderSelect(borders))
        if backgrounds:
            self.add_item(BackgroundSelect(backgrounds))

    async def update(self, interaction: discord.Interaction):

        total_pages = max(1, math.ceil(len(self.all_items) / self.per_page))

        if self.page >= total_pages:
            self.page = total_pages - 1

        page_items = paginate_items(self.all_items, self.page, self.per_page)
        self.current_items = page_items

        # rebuild UI
        self.clear_items()
        self._build_selects(page_items)
        self.add_item(EquipButton())
        self.add_item(PrevPageButton())
        self.add_item(NextPageButton())

        buffer = await generate_inventory(
            items=page_items,
            userId=str(self.user_id),
            page=self.page,
            total_pages=total_pages,
        )

        file = discord.File(buffer, filename="inventory.png")

        await interaction.response.edit_message(
            attachments=[file],
            view=self,
        )
