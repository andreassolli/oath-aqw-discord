import discord

from firebase_client import db


class ServerSelectView(discord.ui.View):
    def __init__(self, ticket_name: str, servers: list[dict], parent_view):
        super().__init__(timeout=60)
        self.ticket_name = ticket_name
        self.parent_view = parent_view
        self.selected_server = None

        self.add_item(ServerSelect(servers))


class ServerSelect(discord.ui.Select):
    def __init__(self, servers: list[dict]):
        options = [
            discord.SelectOption(
                label=server["sName"],
                value=server["sName"],
                description=f"{server['iCount']}/{server['iMax']} players",
            )
            for server in servers
        ]

        super().__init__(
            placeholder="Select Server",
            min_values=1,
            max_values=1,
            options=options[:25],
            row=1,
        )

    async def callback(self, interaction: discord.Interaction):
        view: ServerSelectView = self.view
        selected = self.values[0]

        # Save to DB
        doc_ref = db.collection("tickets").document(view.ticket_name)
        doc_ref.update({"server": selected})

        # Update embed (reuse your existing function)
        await view.parent_view._update_ticket_embed(interaction)

        await interaction.response.edit_message(
            content=f"✅ Server updated to **{selected}**", view=None
        )
