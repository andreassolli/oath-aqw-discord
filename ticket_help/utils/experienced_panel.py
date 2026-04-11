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
            "Are you experienced with ultras, and want to apply to gain a certificate?\nClick the button below to start your application.\n\n"
            "📝 You will need to answer **5 questions** per certificate.\n"
            "⚠️ Make sure to answer carefully.\nA Certification Assessor will review your application and contact you for a trial if needed.\n"
            "Need some tips? [Here is a visual representation of taunting as Lord of Order ⚖️](https://youtu.be/hahe9_HhDZA)\n\n"
            "*Certifications allows you to help if 'Certified Only' is toggled on by the requester. (Only **Gramiel and Speaker** for now)*"
        ),
        color=discord.Color.blurple(),
    )
    embed.set_footer(text="❗️Make sure to copy your answers in case anything happens.")

    await channel.send(embed=embed, view=StartApplicationView())
