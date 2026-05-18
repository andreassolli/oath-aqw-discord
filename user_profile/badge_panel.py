from pathlib import Path

import discord

from config import BADGE_CHANNEL_ID
from panels.badges_panel import BadgesLayout

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


async def setup_verification_panel(client: discord.Client):
    print("Running badge panel setup...")

    channel = client.get_channel(BADGE_CHANNEL_ID)

    if channel is None:
        channel = await client.fetch_channel(BADGE_CHANNEL_ID)

    if not isinstance(channel, discord.TextChannel):
        print("❌ Badges channel not found or not a text channel.")
        return

    async for msg in channel.history(limit=3):
        if msg.author == client.user:
            await msg.delete()

    layout = BadgesLayout()
    await channel.send(view=layout)
