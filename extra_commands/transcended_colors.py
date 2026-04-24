import discord

from config import (
    ASCENDED_ROLE_CHANNEL_ID,
    MIDNIGHT_MOSS,
    ROYAL_VANGUARD,
    TRANSCENDED_ROLE_ID,
    VERDANT_EMBER,
)

COLOR_ROLES = [MIDNIGHT_MOSS, VERDANT_EMBER, ROYAL_VANGUARD]


class ColorRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def handle_role_toggle(
        self,
        interaction: discord.Interaction,
        role_id: int,
        add_msg: str,
        remove_msg: str,
    ):
        guild = interaction.guild
        user = interaction.user

        if guild is None or not isinstance(user, discord.Member):
            return

        transcended_role = guild.get_role(TRANSCENDED_ROLE_ID)
        target_role = guild.get_role(role_id)

        if transcended_role is None or target_role is None:
            await interaction.response.send_message(
                "Role configuration error. Please contact an admin.",
                ephemeral=True,
            )
            return

        if transcended_role not in user.roles:
            await interaction.response.send_message(
                "You must be **Transcended** to claim this role.",
                ephemeral=True,
            )
            return

        if target_role in user.roles:
            await user.remove_roles(target_role)
            await interaction.response.send_message(remove_msg, ephemeral=True)
            return

        roles_to_remove = [r for r in user.roles if r.id in COLOR_ROLES]
        if roles_to_remove:
            await user.remove_roles(*roles_to_remove)

        await user.add_roles(target_role)
        await interaction.response.send_message(add_msg, ephemeral=True)

    @discord.ui.button(
        label="🌿 Midnight Moss",
        style=discord.ButtonStyle.secondary,
        custom_id="midnight_moss_button",
    )
    async def midnight_moss(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.handle_role_toggle(
            interaction,
            MIDNIGHT_MOSS,
            "🌿 You are now cloaked in **Midnight Moss**.",
            "🌑 The forest fades… your **Midnight Moss** role has been removed.",
        )

    @discord.ui.button(
        label="🌾 Verdant Ember",
        style=discord.ButtonStyle.secondary,
        custom_id="verdant_ember_button",
    )
    async def verdant_ember(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.handle_role_toggle(
            interaction,
            VERDANT_EMBER,
            "🔥 You are now enveloped in the flames of **Verdant Ember**.",
            "🔥 The fire is extinguished... **Verdant Ember** has been removed.",
        )

    @discord.ui.button(
        label="🛡️ Royal Vanguard",
        style=discord.ButtonStyle.secondary,
        custom_id="royal_vanguard_button",
    )
    async def royal_vanguard(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.handle_role_toggle(
            interaction,
            ROYAL_VANGUARD,
            "🛡️ You stand among the **Royal Vanguard**.",
            "🗡️ You step down from the **Royal Vanguard**.",
        )


async def setup_color_panel(client: discord.Client):
    channel = client.get_channel(ASCENDED_ROLE_CHANNEL_ID)

    if channel is None:
        channel = await client.fetch_channel(ASCENDED_ROLE_CHANNEL_ID)

    if not isinstance(channel, discord.TextChannel):
        return

    # Delete old bot messages (optional)
    async for msg in channel.history(limit=5):
        if msg.author == client.user:
            await msg.delete()

    embed = discord.Embed(
        title="Transcended Supporters of the Realm",
        description=(
            "By supporting our discord and guild, you have proven your loyalty to the community and our server. We are forever grateful for your contributions! As a token of our gratitude, feel free to select any of the exlusive colors, granted only to those who transcend.\n"
            "To claim your color:\n"
            "React below with the emblem that calls to your spirit.\n"
            "Only one Gradient Color Role per sworn booster—choose wisely, for it shall mark your eternal pledge!\n\n"
            f"🌿 <@&{MIDNIGHT_MOSS}>\n"
            "Drift into the depths with this shadowed verdance, where midnight bleeds into living green - an echo of ancient forests breathing beneath the dark.\n"
            "\n\n"
            f"🌾 <@&{VERDANT_EMBER}>\n"
            "Let life and flame entwine in this smoldering verdure, where wild growth meets a slow-burning blaze - an untamed force that thrives between renewal and ruin.\n"
            "\n\n"
            f"🛡️ <@&{ROYAL_VANGUARD}>\n"
            "Stand at the forefront of glory with this radiant crimson and pure white, a banner of unyielding resolve - where honor marches first, and legends are forged in its wake.\n"
            "\n\n"
            "Check back here later, as there is more to come!\n"
        ),
        color=discord.Color.gold(),
    )
    file = discord.File("assets/oath-logo.png", filename="oath-logo.png")
    embed.set_thumbnail(url="attachment://oath-logo.png")
    embed.set_footer(text="Only available to those supporting through Ko-Fi ☕️")

    await channel.send(file=file, embed=embed, view=ColorRoleView())
