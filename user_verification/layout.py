import discord


class TestLayout(discord.ui.LayoutView):
    def __init__(self):
        super().__init__()

        self.container1 = discord.ui.Container(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="https://avatars.githubusercontent.com/u/77593673?s=128",
                ),
            ),
            discord.ui.TextDisplay(content="Example components:"),
            discord.ui.Section(
                discord.ui.TextDisplay(content="\nButtons"),
                accessory=discord.ui.Button(
                    style=discord.ButtonStyle.primary,
                    label="Test",
                    custom_id="947bd8ccd1ec439caa2309b0d373b65d",
                ),
            ),
        )

        self.add_item(self.container1)
