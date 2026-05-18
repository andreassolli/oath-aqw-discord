import discord

from config import SPAM_CMD_CHANNEL_ID, TICKET_CHANNEL_ID
from panels.test_view import TicketCreateView
from ticket_help.panels.server_fetch import fetch_servers


async def setup_ticket_panel(client: discord.Client):
    channel = client.get_channel(SPAM_CMD_CHANNEL_ID)

    if not channel:
        print("❌ Ticket panel channel not found. Check TICKET_CHANNEL_ID.")
        return

    async for msg in channel.history(limit=5):
        if (
            msg.author == client.user
            and msg.embeds
            and msg.embeds[0].title == "🎫 Need help?"
        ):
            await msg.delete()

    embed = discord.Embed(
        title="🎫 Need help?",
        description="Make sure to read [Creating Tickets, how to & rules](https://discord.com/channels/1455651278590972019/1473074765182009468) before creating a ticket. \nClick the button below to get started.",
        color=discord.Color(0xD8C49B),
    )

    file = discord.File("assets/bountyboard0.png", filename="bountyboard0.png")
    embed.set_image(url="attachment://bountyboard0.png")

    await channel.send(file=file, embed=embed, view=TicketPanelView())


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.primary)
    async def create_ticket(self, interaction: discord.Interaction, _):
        servers = await fetch_servers()
        await interaction.response.defer(ephemeral=True)

        view = TicketCreateView(servers)

        await interaction.followup.send(
            "Select the type for this ticket:",
            view=view,
            ephemeral=True,
        )
