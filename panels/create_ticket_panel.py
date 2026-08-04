import discord

from config import TICKET_CHANNEL_ID
from panels.test_view import TicketCreateView
from ticket_help.panels.server_fetch import fetch_servers
from firebase_client import db
from datetime import datetime
from zoneinfo import ZoneInfo

def world_times():
    return {
        "SEA": datetime.now(ZoneInfo("Asia/Singapore")).strftime("%H:%M"),
        "EU": datetime.now(ZoneInfo("Europe/Berlin")).strftime("%H:%M"),
        "NA": datetime.now(ZoneInfo("America/New_York")).strftime("%H:%M"),
    }

async def setup_new_tickets(client):
    channel = client.get_channel(TICKET_CHANNEL_ID)

    if not channel:
        return

    view = await build_ticket_layout()

    msg = await channel.fetch_message(1533851176938897541)
    await msg.edit(view=view)

TRIPLE_CLEAR_BOSSES = {
    "TimeInn Trio",
    "Void Trio",
    "Legion Daily Exercise 2-4",
    "Temple Shrine",
    "Void Aura (mem)",
    "Void Aura (non mem)"
}

async def build_ticket_layout():
    stats = (
        db.collection("stats")
        .document("boss_clears")
        .get()
        .to_dict()
        or {}
    )

    total_completed = stats.get("total_completed", 0)
    total_points = stats.get("total_points", 0)

    total_clears = 0
    for boss, clears in stats.items():
        if boss in ["total_clears", "total_completed", "total_points"]:
            continue

        multiplier = 3 if boss in TRIPLE_CLEAR_BOSSES else 1
        total_clears += clears * multiplier

    return CreateTicketLayout(
        total_completed=total_completed,
        total_points=total_points,
        total_clears=total_clears,
    )

class CreateTicketLayout(discord.ui.LayoutView):
    def __init__(self, total_completed: int, total_points: int, total_clears: int):

        super().__init__(timeout=None)

        self.container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bountyboard0.png",
                ),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164>** Ticket Stats** (Since Feb. '26)"
            ),
            discord.ui.TextDisplay(
                content=(
                    f">>> <:complete_ticket:1505157129252634706> **{total_completed}** tickets completed\n"
                    f">>> <:medal:1505158451179819119> **{total_points}** points awarded"
                    f">>> <:claiming:1505158455412002846> **{total_clears}** bosses slain"
                )
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
                    content=">>> <a:sparks:1505157330055069706> Create a ticket by clicking the '**Create Ticket**' button!\nHelpers will be with you shortly to help you ❤️"
                ),
                accessory=CreateTicketButton(),
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
            emoji=discord.PartialEmoji(name="oathticket", id=1534027556297248859),
        )


class CreateTicketButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Create Ticket",
            style=discord.ButtonStyle.primary,
            emoji=discord.PartialEmoji(name="claiming", id=1505158455412002846),
            custom_id="create_ticket_button",
        )

    async def callback(self, interaction: discord.Interaction):
        servers = await fetch_servers()
        await interaction.response.defer(ephemeral=True)

        view = TicketCreateView(servers)

        times = world_times()

        await interaction.followup.send(
            f"Current time around the world 🌍\n"
            f"<:sea:1534042598937854092> SEA: `{times['SEA']}`\n"
            f"<:eu:1534042577979048076> EU: `{times['EU']}`\n"
            f"<:na:1534042597100617858> NA: `{times['NA']}`\n\n"
            "Select the type for this ticket:",
            view=view,
            ephemeral=True,
        )
