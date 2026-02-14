import discord

from config import TICKET_CHANNEL_ID

from .panel_view import TicketPanelView


async def setup_ticket_panel(client: discord.Client):
    channel = client.get_channel(TICKET_CHANNEL_ID)

    if not channel:
        print("❌ Ticket panel channel not found. Check TICKET_CHANNEL_ID.")
        return

    async for msg in channel.history(limit=3):
        if msg.author == client.user:
            await msg.delete()

    embed = discord.Embed(
        title="🎫 Need help?",
        description="Click the button below to create a ticket.",
        color=discord.Color.blurple(),
    )

    embed.set_image(
        url="https://www.artix.com/media/6577/wallpaper_yokaidragons2_pc.png"
    )

    await channel.send(embed=embed, view=TicketPanelView())
