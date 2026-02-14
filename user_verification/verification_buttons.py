import discord

from user_verification.verification_modal import VerificationModal


class VerificationButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify me", style=discord.ButtonStyle.success, emoji="✅")
    async def verify(self, interaction: discord.Interaction, _):
        await interaction.response.send_modal(VerificationModal(action="verify"))

    @discord.ui.button(
        label="I want to join Oath", style=discord.ButtonStyle.primary, emoji="🛡️"
    )
    async def join_guild(self, interaction: discord.Interaction, _):
        await interaction.response.send_modal(VerificationModal(action="join"))
