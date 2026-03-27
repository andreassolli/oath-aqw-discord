import random

import discord
from firebase_admin import firestore

from config import EXPERIENCED_HELPER_ROLE_ID, TICKET_CATEGORY_ID
from firebase_client import db
from ticket_help.tickets.embed_utils import build_ticket_embed
from ticket_help.tickets.ids import get_next_ticket_id
from ticket_help.tickets.utils import set_active_ticket
from ticket_help.tickets.views import TicketActionView


class SimpleTicketModal(discord.ui.Modal, title="Create Practice Ticket"):
    def __init__(self, ticket_type: str, server: str, bosses: list[str], username: str):
        super().__init__(title=f"Create {ticket_type.capitalize()} Ticket")

        self.type = ticket_type
        self.server = server

        self._preset_bosses = bosses

        self.username = discord.ui.TextInput(
            label="Username",
            required=True,
            default=username or "",
        )

        self.notes = discord.ui.TextInput(
            label="Any specific stuff you need to practice?",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000,
        )

        self.add_item(self.username)
        self.add_item(self.notes)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            return

        ticket_id = get_next_ticket_id()
        ticket_name = f"practice-{ticket_id:03d}"
        channel_name = f"「🎫」{ticket_name}"

        category = guild.get_channel(TICKET_CATEGORY_ID)

        helper_role = guild.get_role(EXPERIENCED_HELPER_ROLE_ID)
        bosses = self._preset_bosses
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True
            ),
        }

        if helper_role:
            overwrites[helper_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True
            )

        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
        )

        room_value = str(random.randint(11111, 99999))
        db.collection("tickets").document(ticket_name).set(
            {
                "ticket_id": ticket_id,
                "channel_id": channel.id,
                "user_id": interaction.user.id,
                "bosses": bosses,
                "points": 2,
                "max_claims": 3,
                "claimers": [],
                "username": self.username.value,
                "room": room_value,
                "status": "open",
                "type": "extra practice",
                "server": self.server,
                "created_at": firestore.SERVER_TIMESTAMP,
                "reping_helpers": True,
                "reminder_sent": False,
                "auto_closed": False,
            }
        )

        embed = build_ticket_embed(
            requester_id=interaction.user.id,
            bosses=bosses,
            points=2,
            username=self.username.value,
            room=str(room_value),
            max_claims=3,
            claimers=[],
            guild=interaction.guild,
            type=self.type,
            server=self.server,
            total_kills=str(0),
            drops=[],
        )

        allowed_mentioning = discord.AllowedMentions(
            users=True, roles=True, everyone=False
        )

        message = await channel.send(
            embed=embed,
            view=TicketActionView(
                ticket_name=ticket_name,
                max_claims=3,
                room=str(room_value),
                bosses=bosses,
            ),
            allowed_mentions=allowed_mentioning,
        )
        db.collection("tickets").document(ticket_name).update(
            {"message_id": message.id}
        )

        set_active_ticket(interaction.user.id, ticket_name)
        await interaction.followup.send(
            f"✅ Ticket created: {channel.mention}", ephemeral=True
        )

        try:
            await message.pin(reason="Ticket information")
        except discord.Forbidden:
            # Bot is missing 'Manage Messages'
            pass
