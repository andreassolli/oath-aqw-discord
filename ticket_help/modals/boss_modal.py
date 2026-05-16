import discord

from firebase_client import db
from ticket_help.new_panel.ticket_panel import TicketLayout


class ChangeBossModal(discord.ui.Modal, title="Change Bosses"):
    def __init__(
        self, ticket_name: str, bosses: dict[str, str], current: dict[str, str]
    ):
        super().__init__()

        options = []
        for boss in bosses:
            option = discord.CheckboxGroupOption(
                label=boss.get("name"),
                value=boss.get("name"),
                default=boss.get("name") in current,
            )
            options.append(option)

        self.boss_selection = discord.ui.Label(
            text="Select the bosses for this ticket",
            component=discord.ui.CheckboxGroup(
                options=options,
                required=True,
            ),
        )
        self.add_item(self.boss_selection)
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
            claimer_roles = ticket_data.get("claimer_roles", {})
            total_kills = ticket_data.get("total_kills", "0")
            layout = TicketLayout(
                requester_id=ticket_data["user_id"],
                bosses=ticket_data["bosses"],
                points=ticket_data["points"],
                username=ticket_data["username"],
                room=ticket_data["room"],
                max_claims=ticket_data["max_claims"],
                claimers=ticket_data["claimers"],
                guild=interaction.guild,
                type=ticket_data["type"],
                server=ticket_data["server"],
                total_kills=total_kills,
                claimer_roles=claimer_roles,
                ticket_name=self.ticket_name,
            )

            await message.edit(view=layout)

        except discord.NotFound:
            pass

    async def on_submit(self, interaction: discord.Interaction):
        doc_ref = db.collection("tickets").document(self.ticket_name)
        doc_ref.update({"bosses": self.boss_selection.component.values})
        await self._update_ticket_embed(interaction)
        await interaction.response.send_message(
            f"Current bosses: {', '.join(self.boss_selection.component.values)}",
            ephemeral=True,
        )
