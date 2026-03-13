import discord

from inventory.background_select import BackgroundSelect
from inventory.border_select import BorderSelect
from inventory.equip_button import EquipButton


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
