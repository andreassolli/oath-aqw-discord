import discord


class ServerSelect(discord.ui.Select):
    def __init__(self, servers: list[dict]):

        options = [
            discord.SelectOption(
                label=server["sName"],
                value=server["sName"].lower(),
                description=f"{server['iCount']}/{server['iMax']} players",
            )
            for server in servers
        ]

        super().__init__(
            placeholder="Select Server",
            min_values=1,
            max_values=1,
            options=options[:25],  # Discord limit
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_server = self.values[0]
        await interaction.response.defer()
