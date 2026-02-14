import discord

from .embed_class import build_class_embed
from .utils import get_class_image, get_classes_for_boss


class BossButton(discord.ui.Button[discord.ui.View]):
    def __init__(
        self,
        *,
        boss_key: str,
        label: str,
        class_name: str,
    ):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary,
        )

        self.boss_key = boss_key
        self.class_name = class_name  # canonical name

    async def callback(self, interaction: discord.Interaction):

        # 🔥 Pull class setup for this boss
        result = await get_classes_for_boss(self.boss_key)

        class_data = result.get(self.class_name)

        if not class_data:
            return await interaction.response.send_message(
                f"❌ No setup found for **{self.class_name}** against **{self.label}**.",
                ephemeral=True,
            )

        # 🔥 Get image (falls back to "No Class" automatically)
        image_url = get_class_image(self.class_name)

        embed = build_class_embed(
            class_name=f"{self.class_name} — {self.label}",
            general_loadout=class_data,
            consumables=class_data,
            image_url=image_url,
        )

        await interaction.response.edit_message(embed=embed, view=self.view)
