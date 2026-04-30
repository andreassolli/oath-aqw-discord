import discord

SPAM_OPTIONS = [
    "Custom",
    "Middle",
    "Left",
    "Right",
    "All",
]


class SpamSelect(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(
                label=spam_option,
                value=spam_option
                if spam_option == "Custom"
                else f"{spam_option} TempleShrine",
                description=spam_option if spam_option == "Custom" else "TempleShrine",
            )
            for spam_option in SPAM_OPTIONS
        ]

        super().__init__(
            placeholder="Select spam type",
            min_values=1,
            max_values=1,
            options=options[:25],  # Discord limit
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_bosses = self.values[0]
        await interaction.response.defer()
