import discord

from config import ASCENDED_ROLE_CHANNEL_ID, MIDNIGHT_MOSS, TRANSCENDED_ROLE_ID


class ColorRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🌿 Midnight Moss",
        style=discord.ButtonStyle.secondary,
        custom_id="midnight_moss_button",
    )
    async def midnight_moss(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild = interaction.guild
        user = interaction.user

        if guild is None or not isinstance(user, discord.Member):
            return

        transcended_role = guild.get_role(TRANSCENDED_ROLE_ID)
        moss_role = guild.get_role(MIDNIGHT_MOSS)

        if transcended_role is None or moss_role is None:
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

        for role in user.roles:
            if role.id in [MIDNIGHT_MOSS]:
                await user.remove_roles(role)
                await interaction.response.send_message(
                    "🌑 The forest fades… your **Midnight Moss** role has been removed.",
                    ephemeral=True,
                )
        else:
            await user.add_roles(moss_role)
            await interaction.response.send_message(
                "🌿 You are now cloaked in **Midnight Moss**.",
                ephemeral=True,
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
            "-\n\n"
            "Check back here later, as there is more to come!\n"
        ),
        color=discord.Color.gold(),
    )
    file = discord.File("assets/oath-logo.png", filename="oath-logo.png")
    embed.set_thumbnail(url="attachment://oath-logo.png")
    embed.set_footer(text="Only available to those supporting through Ko-Fi ☕️")

    await channel.send(file=file, embed=embed, view=ColorRoleView())
