import discord

from config import VERIFICATION_CHANNEL_ID
from panels.welcome_panel import WelcomeLayout


async def setup_verification_panel(client: discord.Client):
    channel = client.get_channel(VERIFICATION_CHANNEL_ID)

    if not isinstance(channel, discord.TextChannel):
        print("❌ Verification channel not found. Check VERIFICATION_CHANNEL_ID.")
        return

    async for msg in channel.history(limit=3):
        if msg.author == client.user:
            await msg.delete()

    layout = WelcomeLayout()

    await channel.send(view=layout)
