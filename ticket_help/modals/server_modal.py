import discord

from firebase_client import db


class ServerModal(discord.ui.Modal, title="Change Server"):
    def __init__(self, ticket_name: str, servers: list[dict], current: str):
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
        self.ticket_name = ticket_name

    async def _update_ticket_embed(self, interaction: discord.Interaction):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc = doc_ref.get()
        if not doc.exists:
            return

        ticket_data = doc.to_dict()
        message_id = ticket_data.get("message_id")
        if not message_id:
            return

        try:
            message = await interaction.channel.fetch_message(message_id)
            layout = build_ticket_layout(
                ticket_data,
                interaction.guild,
            )

            await message.edit(view=layout)

        except discord.NotFound:
            pass

    async def on_submit(self, interaction: discord.Interaction):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc_ref.update({"server": self.server.component.values[0]})
        await self._update_ticket_embed(interaction)
        await interaction.response.send_message(
            f"Server: {self.server.component.values[0]}", ephemeral=True
        )
