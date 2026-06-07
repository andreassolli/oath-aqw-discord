import discord

from firebase_client import db
from ticket_help.utils.message_logging import log_ticket_message_event


class ServerModal(discord.ui.Modal, title="Change Server"):
    def __init__(self, layout, ticket_name: str, servers: list[dict], current: str):
        super().__init__()
        self.layout = layout

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
        self.ticket_name = ticket_name

    async def on_submit(self, interaction: discord.Interaction):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc_ref.update({"server": self.server.component.values[0]})
        await self.layout.refresh(interaction)

        return await interaction.response.send_message(
            f"Server changed to `{self.server.component.values[0]}` by {interaction.user.mention}."
        )
