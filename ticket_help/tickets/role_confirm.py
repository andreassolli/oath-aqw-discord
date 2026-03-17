import discord

from .role_select import OPTIONS


class ConfirmButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Confirm Selection",
            style=discord.ButtonStyle.success,
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view

        if not view.selected_role:
            return await interaction.response.send_message(
                "Please select a role first.",
                ephemeral=True,
            )

        role = view.selected_role

        await interaction.response.send_message(
            f"✅ **Selected Role:**\n**{role}** → {OPTIONS[role]}",
            ephemeral=True,
        )
