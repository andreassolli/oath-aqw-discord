import discord

from config import ROLES_CHANNEL_ID
from firebase_client import db
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

        await interaction.response.send_message(
            "Select which application you want to apply for:",
            view=ApplicationSelectView(user_data),
            ephemeral=True,
        )


async def setup_application_panel(client: discord.Client):
    channel = client.get_channel(ROLES_CHANNEL_ID)

    if channel is None:
        channel = await client.fetch_channel(ROLES_CHANNEL_ID)

    if not isinstance(channel, discord.TextChannel):
        return

    # Delete old bot messages (optional)
    async for msg in channel.history(limit=5):
        if msg.author == client.user:
            await msg.delete()

    embed = discord.Embed(
        title="Ultra Certificate Application",
        description=(
            "Think you know your ultras? Apply for a certificate!\n\n"
            "📝 Answer 5 questions for the selected boss.\n"
            "⚠️ Speaker, Gramiel and Drakath requires a Trial as well.\n"
            "💰 Speaker and Gramiel rewards <:oathcoin:1462999179998531614>3750, Drakath <:oathcoin:1462999179998531614>2500, rest <:oathcoin:1462999179998531614>1950.\n\n"
            "📌 Tips: \n"
            "- <:gramiel:1492231304601796658> [Gramiel with Lillicht chart 📊️](https://youtu.be/O9PZnXxXClQ?si=4DZBuNmSwG1nqdwK) \n"
            "- <:malgor:1492231505668341860> [Speaker as Lord of Order ⚖️](https://youtu.be/hahe9_HhDZA) \n"
            "- <:malgor:1492231505668341860> [Speaker as ArchPaladin 🛡️](https://youtu.be/ftgaITjXdt8?si=tyILn2PjFQ7bqI6O) \n"
            "- <:dage:1492231405067964627> [Dage as Chaos Avenger/Classic Ninja 🥷](https://youtu.be/hJK9o-yIz9I)\n\n"
            "Use the command `/view-applications` to view your application statuses.\n\n"
        ),
        color=discord.Color.blurple(),
    )
    embed.set_footer(
        text="❗️Certifications allows you to help if 'Certified Only' is toggled on by the requester. (Only Gramiel and Speaker for now, rest will be enabled very soon!)"
    )

    await channel.send(embed=embed, view=StartApplicationView())
