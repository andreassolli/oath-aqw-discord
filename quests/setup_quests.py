import discord

from config import GAMBA_UPDATES_CHANNEL_ID
from panels.quests_panel import QuestsLayout

async def setup_quests(client: discord.Client):
    channel = client.get_channel(GAMBA_UPDATES_CHANNEL_ID)

    if channel is None:
        try:
            channel = await client.fetch_channel(GAMBA_UPDATES_CHANNEL_ID)
        except Exception as e:
            print(f"❌ Failed to fetch quest channel: {e}")
            return

    view = QuestsLayout()

    async for msg in channel.history(limit=10):
        if (
            msg.author == client.user
            and msg.components
        ):
            await msg.edit(view=view)
            return

    await channel.send(view=view)
