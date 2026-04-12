import discord

from config import OFFICER_CHANNEL_ID
from user_verification.verification_modal import VerificationModal


class VerificationButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify me", style=discord.ButtonStyle.success, emoji="✅")
    async def verify(self, interaction: discord.Interaction, _):
        account_age = (discord.utils.utcnow() - interaction.user.created_at).days
        if account_age < 10:
            guild = interaction.guild
            if not guild:
                return
            oathsword_channel = guild.get_channel(OFFICER_CHANNEL_ID)
            if oathsword_channel and isinstance(oathsword_channel, discord.TextChannel):
                await oathsword_channel.send(
                    f"{interaction.user.mention} is trying to verify but their account is too new."
                )

            await interaction.response.send_message(
                "Your account was recently created. You cannot verify at this momeny.",
                ephemeral=True,
            )
            return
        await interaction.response.send_modal(VerificationModal(action="verify"))

    @discord.ui.button(
        label="I want to join Oath", style=discord.ButtonStyle.primary, emoji="🛡️"
    )
    async def join_guild(self, interaction: discord.Interaction, _):
        account_age = (discord.utils.utcnow() - interaction.user.created_at).days
        if account_age < 10:
            guild = interaction.guild
            if not guild:
                return
            oathsword_channel = guild.get_channel(OFFICER_CHANNEL_ID)
            if oathsword_channel and isinstance(oathsword_channel, discord.TextChannel):
                await oathsword_channel.send(
                    f"{interaction.user.mention} is trying to verify but their account is too new."
                )

            await interaction.response.send_message(
                "Your account was recently created. You cannot verify at this momeny.",
                ephemeral=True,
            )
            return
        await interaction.response.send_modal(VerificationModal(action="join"))
