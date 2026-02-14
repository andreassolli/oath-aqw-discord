import discord

from .boss_buttons import BossButton


class BossSetupView(discord.ui.View):
    def __init__(
        self,
        *,
        class_name: str,
        boss_types: dict[str, str],
        boss_sheets: dict[str, str],
    ):
        super().__init__(timeout=120)

        self.class_name = class_name
        self.boss_types = boss_types

        for boss_key, boss_label in boss_types.items():
            self.add_item(
                BossButton(
                    boss_key=boss_key,
                    label=boss_label,
                    class_name=class_name,
                )
            )
