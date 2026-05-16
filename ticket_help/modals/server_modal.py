import discord


class ServerModal(discord.ui.Modal, title="Change Server"):
    def __init__(self, servers: list[dict], current: str):
        super().__init__()
        options = [
            discord.SelectOption(
                label=server["sName"],
                value=server["sName"],
                description=f"{server['iCount']}/{server['iMax']} players",
            )
            for server in servers
        ]
        self.server = discord.ui.Label(
            text="Select the server you want to change to",
            component=discord.ui.Select(
                placeholder=current,
                options=options,
            ),
        )
        self.add_item(self.server)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Server: {self.server.component.values[0]}", ephemeral=True
        )
