import discord

from config import INITIATE_ROLE_ID, OFFICER_CHANNEL_ID
from extra_commands.officer_application.modal import OfficerApplicationModal
from user_verification.verification_modal import VerificationModal

class OfficerApplicationLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        self.container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/welcome.png",
                ),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164>** Apply for Officer**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(">>> <a:arrow:1505157327584624712> Enjoying your time and want to help make our community better? Apply now!\nMust be in Oath, and been in Discord minimum a month."
                ),
                accessory=ApplicationButton(),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164>** Join the guild**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content="> <:star:1503523567898460311> Come hang out with us in game, participate in guild-only events and screenshots. Click '**Join Oath**' to get started!"
                ),
                accessory=JoinGuildButton(),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164> **Get access to the discord**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content="> <a:redcheck:1503523456468254991> Verify by entering your AQW username, and get access to the rest of the discord. Click '**Verify**' to get started!"
                ),
                accessory=VerifyButton(),
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bright_separator.png",
                ),
            ),
            accent_colour=discord.Colour(7344907),
        )

        self.add_item(self.container1)


class ApplicationButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Apply",
            style=discord.ButtonStyle.primary,
            emoji=discord.PartialEmoji(
                name="whiteshield",
                id=1546658412094296194,
            ),
            custom_id="officer_application_button",
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            return
        guild_role = guild.get_role(INITIATE_ROLE_ID)
        member = guild.get_member(interaction.user.id)
        if not member or member.joined_at is None:
            return
        account_age = (discord.utils.utcnow() - member.joined_at).days
        if account_age < 30:
            return await interaction.response.send_message(
                "You need to have been a member of the discord for longer than 30 days in order to apply.",
                ephemeral=True,
            )
        if guild_role not in member.roles:
            return await interaction.response.send_message(
                "You need to be a member of the Oath guild in AQW in order to apply.",
                ephemeral=True,
            )

        await interaction.response.send_modal(OfficerApplicationModal())


class VerifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Verify",
            style=discord.ButtonStyle.primary,
            emoji=discord.PartialEmoji(
                name="verify_button",
                id=1505158460814262464,
            ),
            custom_id="verify_me_button",
        )

    async def callback(self, interaction: discord.Interaction):
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


class JoinGuildButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Join Oath",
            style=discord.ButtonStyle.primary,
            emoji=discord.PartialEmoji(
                name="oath",
                id=1503698814652121118,
            ),
            custom_id="join_oath_button",
        )

    async def callback(self, interaction: discord.Interaction):
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
