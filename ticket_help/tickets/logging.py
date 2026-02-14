import discord
from config import TICKET_LOG_CHANNEL_ID

async def log_ticket_event(client, *, embed: discord.Embed):
    channel = client.get_channel(TICKET_LOG_CHANNEL_ID)
    if channel:
        await channel.send(embed=embed)
