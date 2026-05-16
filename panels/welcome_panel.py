import discord

from config import SPAM_CMD_CHANNEL_ID


async def setup_welcome(client: discord.Client):
    channel = client.get_channel(SPAM_CMD_CHANNEL_ID)

    if not channel:
        print("❌ Ticket panel channel not found. Check TICKET_CHANNEL_ID.")
        return

    await channel.send(view=WelcomeLayout())


class WelcomeLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__()

        self.container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/welcome.png",
                ),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164> **Get access to the discord**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content="> <a:redcheck:1503523456468254991> Verify by entering your AQW username, and get access to the rest of the discord. Click '**Verify**' to get started!"
                ),
                accessory=VerifyButton(),
            ),
            discord.ui.TextDisplay(content="‎"),
            discord.ui.TextDisplay(
                content="<:wing:1503517636695425164>** Join the guild**"
            ),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    content="> <:star:1503523567898460311> Come hang out with us in game, participate in guild-only events and screenshots. Click '**Join Oath**' to get started!"
                ),
                accessory=JoinGuildButton(),
            ),
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://raw.githubusercontent.com/andreassolli/oath-aqw-discord/refs/heads/main/assets/bright_separator.png",
                ),
            ),
            accent_colour=discord.Colour(7344907),
        )

        self.add_item(self.container1)


class VerifyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Verify",
            style=discord.ButtonStyle.primary,
            emoji=discord.PartialEmoji(
                name="verify_button",
                id=1505158460814262464,
            ),
            custom_id="verify_me_button",
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hi")


class JoinGuildButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label=" Join Oath",
            style=discord.ButtonStyle.primary,
            emoji=discord.PartialEmoji(
                name="oath",
                id=1503698814652121118,
            ),
            custom_id="join_oath_button",
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hi")
