import discord


class TestLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__()

        self.container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="",
                ),
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(content="Verify your account below."),
                accessory=VerifyButton(),
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(content="Interested in joining Oath?"),
                accessory=JoinGuildButton(),
            ),
        )

        self.add_item(self.container1)


import discord

from config import OFFICER_CHANNEL_ID
from user_verification.verification_modal import VerificationModal


class VerifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Verify me",
            style=discord.ButtonStyle.success,
            emoji="✅",
            custom_id="verify_me_button",
        )

    async def callback(self, interaction: discord.Interaction):
        account_age = (discord.utils.utcnow() - interaction.user.created_at).days

        if account_age < 10:
            guild = interaction.guild

            if guild:
                officer_channel = guild.get_channel(OFFICER_CHANNEL_ID)

                if officer_channel:
                    await officer_channel.send(
                        f"{interaction.user.mention} tried to verify with a new account."
                    )

            await interaction.response.send_message(
                "Your account is too new to verify.",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(VerificationModal(action="verify"))


class JoinGuildButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="I want to join Oath",
            style=discord.ButtonStyle.primary,
            emoji="🛡️",
            custom_id="join_oath_button",
        )

    async def callback(self, interaction: discord.Interaction):
        account_age = (discord.utils.utcnow() - interaction.user.created_at).days

        if account_age < 10:
            guild = interaction.guild

            if guild:
                officer_channel = guild.get_channel(OFFICER_CHANNEL_ID)

                if officer_channel:
                    await officer_channel.send(
                        f"{interaction.user.mention} tried to join with a new account."
                    )

            await interaction.response.send_message(
                "Your account is too new to apply.",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(VerificationModal(action="join"))
