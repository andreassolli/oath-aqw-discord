import discord

from config import TICKET_CHANNEL_ID
from ticket_help.panels.ticket_counter import build_ticket_counter


async def update_ticket(client: discord.Client):
    channel = client.get_channel(TICKET_CHANNEL_ID)

    if not channel:
        print("❌ Ticket channel not found.")
        return

    embed = await build_ticket_counter(channel.guild)

    async for msg in channel.history(limit=10):
        if (
            msg.author == client.user
            and msg.embeds
            and msg.embeds[0].title == "Ticket stats since January 27th, 2026"
        ):
            await msg.edit(embed=embed)
            return

    await channel.send(embed=embed)
