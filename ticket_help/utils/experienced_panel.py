import discord

from config import ROLE_GROUPS, ROLES_CHANNEL_ID
from firebase_client import db
from panels.roles_panel import RoleLayout
from ticket_help.utils.certified import ApplicationSelectView


class StartApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🤝 Start Application",
        style=discord.ButtonStyle.primary,
        custom_id="start_application_button",
    )
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):

        user_ref = db.collection("users").document(str(interaction.user.id))
        user_doc = user_ref.get()
        user_data = user_doc.to_dict() or {}
        certificate_ban = user_data.get("certificate_ban")
        if certificate_ban:
            return await interaction.response.send_message(
                "You are banned from submitting applications",
                ephemeral=True,
            )
        await interaction.response.send_message(
            "Select which application you want to apply for:",
            view=ApplicationSelectView(user_data),
            ephemeral=True,
        )


async def setup_application_panel(client: discord.Client):
    colors = RoleLayout(
        title="**Choose Your Color Role**",
        image="colors.png",
        description="All Oath members can claim one of these base colors to make your name stand out:",
        role_data=ROLE_GROUPS["color"],
    )
    social = RoleLayout(
        title="**Social Activities**",
        subtitle="Want to socialize with the guildies? :oath:",
        image="social.png",
        description="Click to opt in for notifications based on which social activity you want to be notified about. You can always opt out later!",
        role_data=ROLE_GROUPS["social"],
    )
    notifications = RoleLayout(
        title="**Opt Out of Notifications**",
        subtitle="Getting too many notifications?",
        image="notification.png",
        description="Just remove any roles you don't want notifications from. You can always add them back later!",
        role_data=ROLE_GROUPS["notification"],
    )
    channel = client.get_channel(ROLES_CHANNEL_ID)

    if channel is None:
        channel = await client.fetch_channel(ROLES_CHANNEL_ID)

    if not isinstance(channel, discord.TextChannel):
        return

    embed = discord.Embed(
        title="Ultra Certificate Application",
        description=(
            "Think you know your ultras? Apply for a certificate!\n\n"
            "📝 Answer up to 5 questions for the selected boss.\n"
            "⚠️ Speaker, Gramiel and Darkon requires a Trial as well.\n"
            "💰 Speaker and Gramiel rewards <:oathcoin:1462999179998531614>3750, Darkon <:oathcoin:1462999179998531614>2500, rest <:oathcoin:1462999179998531614>1950.\n\n"
            "🎥 Video tips: \n"
            "- <:gramiel:1492231304601796658> [Gramiel with Lillicht chart 📊️](https://youtu.be/O9PZnXxXClQ?si=4DZBuNmSwG1nqdwK) \n"
            "- <:malgor:1492231505668341860> [Speaker as Lord of Order ⚖️](https://youtu.be/hahe9_HhDZA) \n"
            "- <:malgor:1492231505668341860> [Speaker as ArchPaladin 🛡️](https://youtu.be/ftgaITjXdt8?si=tyILn2PjFQ7bqI6O) \n"
            "- <:dage:1492231405067964627> [Dage as Chaos Avenger/Classic Ninja 🥷](https://youtu.be/hJK9o-yIz9I)\n"
            "- <:drago:1492231338353229985> [Taunting at Drago 👑](https://www.youtube.com/watch?v=o1n94q9vjr8)\n\n"
            "Use the command `/view-applications` to view your application statuses.\n\n"
        ),
        color=discord.Color.blurple(),
    )
    embed.set_footer(
        text="❗️Certifications allows you to help if 'Certified Only' is toggled on by the requester. (Only Gramiel and Speaker for now, rest will be enabled very soon!)"
    )

    # try:
    # color_msg = await channel.fetch_message(1515795016294076487)
    # await color_msg.edit(view=color_layout)
    # except discord.NotFound:
    await channel.send(
        view=colors,
        allowed_mentions=discord.AllowedMentions.none(),
    )
    await channel.send(
        view=social,
        allowed_mentions=discord.AllowedMentions.none(),
    )
    await channel.send(
        view=notifications,
        allowed_mentions=discord.AllowedMentions.none(),
    )
    await channel.send(
        embed=embed,
        view=StartApplicationView(),
        allowed_mentions=discord.AllowedMentions.none(),
    )

    # try:
    #    application_msg = await channel.fetch_message(1515795019372560424)
    #    await application_msg.edit(
    #        embed=embed,
    #        view=StartApplicationView(),
    #    )
    # except discord.NotFound:
    #    application_msg = await channel.send(
    #        embed=embed,
    #        view=StartApplicationView(),
    #    )
