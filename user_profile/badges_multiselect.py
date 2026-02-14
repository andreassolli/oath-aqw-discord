from __future__ import annotations

import discord


class BadgesMultiSelect(discord.ui.Select):
    def __init__(self, badges: list[str]):
        options = [discord.SelectOption(label=badge, value=badge) for badge in badges]

        super().__init__(
            placeholder="Select one or more badges🎖️",
            min_values=1,
            max_values=len(options),
            options=options,
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        if hasattr(self.view, "selected_values"):
            self.view.selected_values = list(self.values)

        if not interaction.response.is_done():
            await interaction.response.defer()
