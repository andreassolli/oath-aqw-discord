import discord

from config import TICKET_INSPECTORS_CHANNEL_ID
from ticket_help.utils.experienced import StartView


async def setup_application_panel(client: discord.Client):
    channel = client.get_channel(TICKET_INSPECTORS_CHANNEL_ID)

    if channel is None:
        channel = await client.fetch_channel(TICKET_INSPECTORS_CHANNEL_ID)

    if not isinstance(channel, discord.TextChannel):
        return

    # Delete old bot messages (optional)
    async for msg in channel.history(limit=5):
        if msg.author == client.user:
            await msg.delete()

    embed = discord.Embed(
        title="Experienced Helper Application",
        description=(
            "Are you experienced with ultras, and want to apply to become an Experienced Helper?\nClick the button below to start your application.\n\n"
            "📝 You will need to answer **10 questions** in total about **Ultra Speaker** and **Ultra Gramiel**, divided into 2 parts.\n"
            "⚠️ Make sure to answer carefully.\nA ticket inspector will review your application and contact you for a trial if needed.\n\n"
            "*Experienced Helpers are able to help if 'Experienced Only' is toggled on by the requester. (Only for **Gramiel and Speaker** for now)*"
        ),
        color=discord.Color.blurple(),
    )

    await channel.send(embed=embed, view=StartView())
