import discord

from config import VERY_TEMP_CHANNEL
from panels.test_view import TicketCreateView
from ticket_help.panels.server_fetch import fetch_servers


async def setup_new_tickets(client: discord.Client):
    channel = client.get_channel(VERY_TEMP_CHANNEL)

    if not channel:
        print("❌ Ticket panel channel not found. Check TICKET_CHANNEL_ID.")
        return

    await channel.send(view=CreateTicketLayout())


class CreateTicketLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        self.container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/tickets.png",
                ),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164>** Tickets, rules and how to**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=">>> <:star:1503523567898460311> Before creating a ticket please read the guide for how they work. Check it out by clicking on '**Ticket Guide**'"
                ),
                accessory=GuideButton(),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164>** Need help with one or more bosses?**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=">>> <a:sparks:1505157330055069706> Create a ticket using the **Create ticket** button!\nHelpers will be with you shortly to help you❤️"
                ),
                accessory=CreateTicketButton(),
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bountyboard0.png",
                ),
            ),
            accent_colour=discord.Colour(7344907),
        )
        self.add_item(self.container1)


class GuideButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            url="https://discord.com/channels/1455651278590972019/1473074765182009468",
            style=discord.ButtonStyle.link,
            label=" Ticket Guide",
            emoji=discord.PartialEmoji(
                name="star",
                id=1503523567898460311,
            ),
        )


class CreateTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Create Ticket",
            style=discord.ButtonStyle.primary,
            custom_id="",
        )

    async def callback(self, interaction: discord.Interaction):
        servers = await fetch_servers()
        await interaction.response.defer(ephemeral=True)

        view = TicketCreateView(servers)

        await interaction.followup.send(
            "Select the type for this ticket:",
            view=view,
            ephemeral=True,
        )
