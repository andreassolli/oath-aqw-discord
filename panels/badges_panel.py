import discord

from config import SPAM_CMD_CHANNEL_ID


async def setup_badges(client: discord.Client):
    channel = client.get_channel(SPAM_CMD_CHANNEL_ID)

    if not channel:
        print("❌ Ticket panel channel not found. Check TICKET_CHANNEL_ID.")
        return

    await channel.send(view=BadgesLayout())


class BadgesLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__()

        self.container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/badges.png",
                ),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503698816300351648>** Apply for profile badges**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=">>> <a:sparks:1503698787754053693> Freshen up your profile card with some neat badges!\nKeep the necessary items in your inventory when applying."
                ),
                accessory=BadgesButton(),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503698816300351648>** Learn more about badges**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content=">>> <:star:1503698784872566886> If you wish to learn more about which badges you can get and what they are, click on '**What are badges?**'"
                ),
                accessory=GuideButton(),
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bright_separator.png",
                ),
            ),
            accent_colour=discord.Colour(7344907),
        )
        self.add_item(self.container1)


class BadgesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Apply for badges",
            style=discord.ButtonStyle.primary,
            emoji=discord.PartialEmoji(
                name="button_badges",
                id=1503826987381162157,
            ),
            custom_id="badges_button",
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hi")


class GuideButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            url="https://discord.com/channels/1455651278590972019/1471212539168686345",
            style=discord.ButtonStyle.link,
            label="What are badges?",
            emoji=discord.PartialEmoji(
                name="star",
                id=1503698784872566886,
            ),
        )
