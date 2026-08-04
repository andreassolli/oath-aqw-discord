import discord

from config import TICKET_CHANNEL_ID
from panels.create_ticket_panel import build_ticket_layout

async def update_ticket_panel(client: discord.Client):
    channel = client.get_channel(TICKET_CHANNEL_ID)

    if not channel:
        return

    view = await build_ticket_layout()

    msg = await channel.fetch_message(1533851176938897541)
    await msg.edit(view=view)
